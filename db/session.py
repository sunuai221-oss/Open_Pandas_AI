# db/session.py

import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Optionnel : charger les variables d'environnement depuis un .env si present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv n'est pas obligatoire pour fonctionner si tout est dans l'env systeme

# Utilisation de PostgreSQL (fallback SQLite possible via DATABASE_URL)
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql+psycopg2://postgres:123@localhost:5432/openpanda'
)
print('DATABASE_URL utilise :', DATABASE_URL)

# Controle du log SQL (True/False)
SQL_ECHO = os.getenv('SQL_ECHO', 'True') == 'True'

try:
    engine = create_engine(
        DATABASE_URL,
        echo=SQL_ECHO,
        future=True,
        connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print('Erreur lors de la connexion a la base :', e)
    raise


@contextmanager
def get_session():
    """Context manager qui garantit la fermeture propre de la session et le rollback en cas d'erreur."""
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Utilisation typique :
# from db.session import get_session
# with get_session() as session:
#     ...
