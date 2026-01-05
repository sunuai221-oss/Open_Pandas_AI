import os
import sys
import tempfile
import subprocess
import pickle
import threading
import time
from pathlib import Path
from typing import Optional
import pandas as pd

# Optional runtime dependency; we degrade gracefully if missing
try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - optional
    psutil = None  # type: ignore

# Import conditionnel du nouvel exécuteur Docker
USE_DOCKER_SANDBOX = os.getenv('USE_DOCKER_SANDBOX', 'false').lower() == 'true'

if USE_DOCKER_SANDBOX:
    try:
        from core.docker_sandbox_executor import get_docker_executor
        DOCKER_AVAILABLE = True
    except ImportError:
        DOCKER_AVAILABLE = False
        print("Docker non disponible, utilisation du mode subprocess")
else:
    DOCKER_AVAILABLE = False

SANDBOX_TIMEOUT_SECONDS = int(os.getenv('SANDBOX_TIMEOUT_SECONDS', '10'))
SANDBOX_MAX_RSS_MB = int(os.getenv('SANDBOX_MAX_RSS_MB', '512'))  # limite mémoire douce (RSS)
SANDBOX_MAX_CPU_SECONDS = float(os.getenv('SANDBOX_MAX_CPU_SECONDS', '15'))  # temps CPU cumulé
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def execute_code(code: str, df: pd.DataFrame):
    """
    Execute generated code inside a sandboxed environment.

    Utilise Docker si disponible et activé (USE_DOCKER_SANDBOX=true),
    sinon fallback vers subprocess pour compatibilité.
    """

    # Mode Docker sécurisé (recommandé)
    if USE_DOCKER_SANDBOX and DOCKER_AVAILABLE:
        try:
            executor = get_docker_executor()
            return executor.execute_code(code, df)
        except Exception as e:
            print(f"Erreur Docker, fallback subprocess: {e}")
            # Fallback vers subprocess en cas d'erreur Docker

    # Mode subprocess (legacy, renforcé)
    return _execute_code_subprocess(code, df)


def _monitor_limits(proc: subprocess.Popen, kill_reason: dict):
    """Surveille mémoire et CPU; tue le process si dépassement.
    Fonctionne uniquement si psutil est disponible.
    """
    if psutil is None:
        return
    try:
        p = psutil.Process(proc.pid)
        start = time.time()
        while True:
            if proc.poll() is not None:
                return
            # Mémoire RSS en MiB
            rss_mb = p.memory_info().rss / (1024 * 1024)
            cpu_time = sum(p.cpu_times()[:2])  # user + system
            if rss_mb > SANDBOX_MAX_RSS_MB:
                kill_reason['reason'] = f"Limite mémoire dépassée: {rss_mb:.0f} MiB > {SANDBOX_MAX_RSS_MB} MiB"
                proc.terminate()
                return
            if cpu_time > SANDBOX_MAX_CPU_SECONDS:
                kill_reason['reason'] = f"Limite CPU dépassée: {cpu_time:.1f}s > {SANDBOX_MAX_CPU_SECONDS}s"
                proc.terminate()
                return
            time.sleep(0.05)
    except Exception:
        # En cas d'erreur du surveillant, on n'empêche pas l'exécution
        return


def _lower_process_priority(proc: subprocess.Popen):
    """Baisse la priorité CPU du processus (best-effort, Windows)."""
    if psutil is None:
        return
    try:
        p = psutil.Process(proc.pid)
        if os.name == 'nt':
            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        else:
            p.nice(10)
    except Exception:
        pass


def _execute_code_subprocess(code: str, df: pd.DataFrame):
    """
    Méthode d'exécution via subprocess (fallback), renforcée:
    - délais d'exécution
    - priorité CPU réduite
    - monitoring mémoire/CPU (best-effort si psutil présent)
    - nettoyage d'environnement (proxies, secrets)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        df_path = tmpdir_path / 'frame.pkl'
        code_path = tmpdir_path / 'snippet.py'
        result_path = tmpdir_path / 'result.pkl'

        df.to_pickle(df_path)
        code_path.write_text(code, encoding='utf-8')

        cmd = [sys.executable, '-m', 'core.sandbox_runner', str(df_path), str(code_path), str(result_path)]

        # Environnement nettoyé
        env = {k: v for k, v in os.environ.items()}
        for k in list(env.keys()):
            if k.upper().endswith('_API_KEY') or k.upper().startswith(('AWS_', 'AZURE_', 'GOOGLE_', 'OPENAI_', 'ANTHROPIC_')):
                env.pop(k, None)
        # Désactive proxies éventuels
        for key in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY', 'http_proxy', 'https_proxy', 'all_proxy', 'no_proxy'):
            env.pop(key, None)
        env.pop('MISTRAL_API_KEY', None)

        creationflags = 0
        if os.name == 'nt':
            creationflags |= getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            creationflags |= getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0)

        killed = {'reason': None}  # type: ignore
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(PROJECT_ROOT),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=creationflags
            )
            _lower_process_priority(proc)
            monitor = threading.Thread(target=_monitor_limits, args=(proc, killed), daemon=True)
            monitor.start()
            try:
                stdout, stderr = proc.communicate(timeout=SANDBOX_TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                proc.terminate()
                return "Erreur lors de l'exécution du code généré : temps d'exécution dépassé."
        finally:
            pass

        stdout = (stdout or '').strip()
        stderr = (stderr or '').strip()

        if killed.get('reason'):
            return f"Erreur lors de l'exécution du code généré : {killed['reason']}"

        if proc.returncode != 0:
            message = stderr or stdout or 'Erreur inconnue retournée par la sandbox.'
            return f"Erreur lors de l'exécution du code généré : {message}"

        if result_path.exists():
            with result_path.open('rb') as handle:
                return pickle.load(handle)

        return stdout or "Le code a été exécuté, mais aucun résultat n'a été produit."
