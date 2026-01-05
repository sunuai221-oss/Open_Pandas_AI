FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /sandbox

# Installation des dépendances minimales pour l'exécution
# openpyxl est inclus pour les opérations Excel futures même si to_excel est bloqué
RUN pip install --no-cache-dir pandas==2.1.4 openpyxl==3.1.5 xlrd==2.0.1

# Copie uniquement les utilitaires nécessaires
COPY core/utils.py /sandbox/
COPY core/sandbox_runner.py /sandbox/

# Utilisateur non-privilégié pour sécurité renforcée
RUN useradd -m -u 1000 sandbox
USER sandbox

# Point d'entrée pour l'exécution du code
ENTRYPOINT ["python", "sandbox_runner.py"]

