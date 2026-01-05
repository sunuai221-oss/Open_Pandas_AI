import argparse
import builtins
import io
import os
import ast
import socket
import pickle
import sys
import traceback
from pathlib import Path

import pandas as pd

from core.utils import (
    calculate_age,
    calculate_days_between,
    extract_year,
    is_valid_email,
    anonymize_phone,
    get_country_code,
    format_currency,
    round_to,
    age_category,
    tenure_years,
    valid_female_percentage,
    average_age_plus1,
    top_3_jobs_under_30,
    female_percentage,
    valid_email_percentage,
    mean_age_females,
    mean_age_males,
)

# Limites configurables
SANDBOX_MAX_RESULT_MB = int(os.getenv('SANDBOX_MAX_RESULT_MB', '8'))

SAFE_BUILTIN_NAMES = [
    'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'float', 'frozenset',
    'int', 'len', 'list', 'max', 'min', 'pow', 'print', 'range', 'reversed',
    'round', 'set', 'slice', 'sorted', 'str', 'sum', 'tuple', 'zip',
    'map', 'filter', 'next', 'Exception', 'ValueError', 'TypeError'
]

SAFE_BUILTINS = {name: getattr(builtins, name) for name in SAFE_BUILTIN_NAMES if hasattr(builtins, name)}


def _deny_io(*_args, **_kwargs):  # Pandas IO/SQL/network operations are blocked
    raise RuntimeError('Operations de lecture/ecriture de fichiers, SQL ou reseau sont desactivees dans la sandbox.')


def _patch_pandas_io():
    # Bloque les fonctions d'entree/sortie pour eviter l'acces FS/ reseau
    blocked = [
        'read_csv', 'read_table', 'read_fwf', 'read_excel', 'read_json', 'read_html',
        'read_parquet', 'read_orc', 'read_feather', 'read_stata', 'read_sas',
        'read_pickle', 'read_sql', 'read_sql_query', 'read_sql_table', 'read_gbq'
    ]
    for name in blocked:
        if hasattr(pd, name):
            setattr(pd, name, _deny_io)


def _disable_network():
    # Supprime variables de proxy pour limiter les sorties
    for key in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY', 'http_proxy', 'https_proxy', 'all_proxy', 'no_proxy'):
        os.environ.pop(key, None)

    def _deny(*_a, **_k):
        raise RuntimeError('Acces reseau desactive dans la sandbox.')

    try:
        socket.socket = _deny  # type: ignore
        socket.create_connection = _deny  # type: ignore
        socket.getaddrinfo = _deny  # type: ignore
    except Exception:
        pass


def _build_environment(df: pd.DataFrame):
    env = {
        '__builtins__': SAFE_BUILTINS,
        'df': df,
        'pd': pd,
        'calculate_age': calculate_age,
        'calculate_days_between': calculate_days_between,
        'extract_year': extract_year,
        'is_valid_email': is_valid_email,
        'anonymize_phone': anonymize_phone,
        'get_country_code': get_country_code,
        'format_currency': format_currency,
        'round_to': round_to,
        'age_category': age_category,
        'tenure_years': tenure_years,
        'valid_female_percentage': valid_female_percentage,
        'average_age_plus1': average_age_plus1,
        'top_3_jobs_under_30': top_3_jobs_under_30,
        'female_percentage': female_percentage,
        'valid_email_percentage': valid_email_percentage,
        'mean_age_females': mean_age_females,
        'mean_age_males': mean_age_males,
    }
    return env


def _validate_code_ast(code: str):
    try:
        tree = ast.parse(code, mode='exec')
    except SyntaxError as e:
        raise RuntimeError(f'SyntaxError dans le code genere: {e}')

    banned_names = {'open', 'eval', 'exec', '__import__', 'compile'}
    banned_modules = {'os', 'sys', 'subprocess', 'socket', 'importlib', 'ctypes', 'pathlib', 'shutil'}

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise RuntimeError('Les importations sont interdites dans la sandbox.')
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name) and f.id in banned_names:
                raise RuntimeError(f"L'appel a {f.id} est interdit dans la sandbox.")
        if isinstance(node, ast.Attribute) and isinstance(node.attr, str) and node.attr.startswith('__'):
            raise RuntimeError('Acces aux attributs dunder interdit (__attr).')
        if isinstance(node, ast.Name) and node.id in banned_modules:
            raise RuntimeError(f"L'utilisation du module/nom '{node.id}' est interdite dans la sandbox.")


def _serialize_result(result, output_path: Path):
    # Limite la taille du resultat pour eviter OOM côté parent
    try:
        payload = pickle.dumps(result)
        max_bytes = SANDBOX_MAX_RESULT_MB * 1024 * 1024
        if len(payload) > max_bytes:
            result = f"Resultat tronque: taille {len(payload)} octets > limite {max_bytes} octets"
            payload = pickle.dumps(result)
    except Exception:
        # Si la serialization echoue, on renvoie le str(result)
        payload = pickle.dumps(str(result))
    with output_path.open('wb') as handle:
        handle.write(payload)


def run_sandbox(frame_path: Path, code_path: Path, output_path: Path):
    """
    Execute le code dans un environnement sandbox (subprocess/Docker).
    Renforcements:
    - ast: interdiction des imports, eval/exec, dunder
    - blocage reseau (socket) et IO pandas
    - limite de taille sur le resultat serialise
    """
    df = pd.read_pickle(frame_path)
    code = code_path.read_text(encoding='utf-8')

    # Durcissement avant compilation
    _disable_network()
    _patch_pandas_io()
    _validate_code_ast(code)

    environment = _build_environment(df)
    sandbox_locals = {}

    buffer = io.StringIO()
    previous_stdout = sys.stdout
    sys.stdout = buffer
    try:
        compiled = compile(code, '<sandbox>', 'exec')
        exec(compiled, environment, sandbox_locals)
    except Exception:
        sys.stdout = previous_stdout
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    finally:
        captured_output = buffer.getvalue()
        sys.stdout = previous_stdout

    result = sandbox_locals.get('result', environment.get('result'))
    if result is None:
        captured_output = captured_output.strip()
        if captured_output:
            result = captured_output
        else:
            result = "Le code a ete execute, mais aucun resultat n'a ete produit."
    _serialize_result(result, output_path)

    if captured_output.strip():
        print(captured_output.strip())


def main():
    parser = argparse.ArgumentParser(description='Execute code in a restricted sandbox environment.')

    # Support des chemins relatifs pour Docker
    if len(sys.argv) == 4 and not sys.argv[1].startswith('/'):
        # Mode Docker : chemins relatifs dans /sandbox/data
        base_path = Path('/sandbox/data')
        frame_path = base_path / sys.argv[1]
        code_path = base_path / sys.argv[2]
        output_path = base_path / sys.argv[3]
    else:
        # Mode subprocess : chemins absolus
        parser.add_argument('frame_path', type=Path, help='Path to the serialized DataFrame input file.')
        parser.add_argument('code_path', type=Path, help='Path to the generated Python code snippet.')
        parser.add_argument('output_path', type=Path, help='Path where the sandbox should persist the result.')
        args = parser.parse_args()
        frame_path = args.frame_path
        code_path = args.code_path
        output_path = args.output_path

    run_sandbox(frame_path, code_path, output_path)


if __name__ == '__main__':
    main()
