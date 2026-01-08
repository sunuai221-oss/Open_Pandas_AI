@echo off
echo ================================
echo   Démarrage de Open_Pandas_AI
echo ================================

REM Aller dans le dossier du projet
cd /d "C:\Users\GAMER PC\NABS\DEV\Open_Pandas_AI"

REM Activer l'environnement virtuel
call .venv\Scripts\activate.bat

REM Lancer Streamlit
streamlit run app.py

REM Pause pour garder la fenêtre ouverte en cas d'erreur
pause
