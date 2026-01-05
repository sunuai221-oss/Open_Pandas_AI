@echo off
cd /d "C:\Users\GAMER PC\NABS\DEV\Open_Pandas_AI"
call .venv\Scripts\activate.bat
set PYTHONPATH=%CD%
streamlit run app.py
pause
