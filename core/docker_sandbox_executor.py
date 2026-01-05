import os
import tempfile
import pickle
import docker
from pathlib import Path
import pandas as pd
from typing import Union

SANDBOX_TIMEOUT_SECONDS = int(os.getenv('SANDBOX_TIMEOUT_SECONDS', '30'))
SANDBOX_IMAGE = os.getenv('SANDBOX_IMAGE', 'openpanda-sandbox:latest')

class DockerSandboxExecutor:
    """
    Executeur securise utilisant des conteneurs Docker ephemeres.
    Chaque execution de code se fait dans un conteneur isole qui est
    automatiquement detruit apres usage.
    """

    def __init__(self):
        try:
            self.docker_client = docker.from_env()
            # Verification que l'image sandbox existe
            self._ensure_sandbox_image()
        except Exception as e:
            raise RuntimeError(f"Impossible de se connecter a Docker: {e}")

    def _ensure_sandbox_image(self):
        """Verifie que l'image sandbox existe, sinon la construit"""
        try:
            self.docker_client.images.get(SANDBOX_IMAGE)
        except docker.errors.ImageNotFound:
            print(f"Construction de l'image sandbox {SANDBOX_IMAGE}...")
            self.docker_client.images.build(
                path=".",
                dockerfile="docker/sandbox.Dockerfile",
                tag=SANDBOX_IMAGE,
                rm=True
            )

    def execute_code(self, code: str, df: pd.DataFrame) -> Union[str, pd.DataFrame, any]:
        """
        Execute le code dans un conteneur Docker ephemere.

        Args:
            code: Code Python a executer
            df: DataFrame a traiter

        Returns:
            Resultat de l'execution ou message d'erreur
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Preparation des fichiers d'echange
            df_path = tmpdir_path / 'frame.pkl'
            code_path = tmpdir_path / 'snippet.py'
            result_path = tmpdir_path / 'result.pkl'

            # Serialisation des donnees
            df.to_pickle(df_path)
            code_path.write_text(code, encoding='utf-8')

            try:
                # Creation et execution du conteneur ephemere
                container = self.docker_client.containers.run(
                    SANDBOX_IMAGE,
                    command=[
                        str(df_path.name),
                        str(code_path.name),
                        str(result_path.name)
                    ],
                    volumes={
                        str(tmpdir_path): {
                            'bind': '/sandbox/data',
                            'mode': 'rw'
                        }
                    },
                    working_dir='/sandbox',
                    detach=True,
                    remove=True,  # Auto-destruction
                    network_mode='none',  # Pas d'acces reseau
                    mem_limit='512m',  # Limite memoire
                    cpu_quota=50000,  # Limite CPU (50%)
                    user='sandbox'  # Utilisateur non-privilegie
                )

                # Attente de la fin d'execution avec timeout
                exit_code = container.wait(timeout=SANDBOX_TIMEOUT_SECONDS)
                logs = container.logs(stdout=True, stderr=True).decode('utf-8')

                if isinstance(exit_code, dict):
                    status_code = exit_code.get('StatusCode', 1)
                else:
                    status_code = exit_code or 1

                if status_code != 0:
                    return f"Erreur lors de l'execution du code genere : {logs}"

                # Recuperation du resultat
                if result_path.exists():
                    with result_path.open('rb') as handle:
                        return pickle.load(handle)

                return logs.strip() or "Le code a ete execute, mais aucun resultat n'a ete produit."

            except docker.errors.ContainerError as e:
                return f"Erreur conteneur : {e}"
            except Exception as e:
                return f"Erreur lors de l'execution du code genere : {e}"

# Instance globale de l'executer
_docker_executor = None


def get_docker_executor():
    """Retourne l'instance singleton de l'executer Docker"""
    global _docker_executor
    if _docker_executor is None:
        _docker_executor = DockerSandboxExecutor()
    return _docker_executor

