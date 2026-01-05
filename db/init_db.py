# db/init_db.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.models import Base
from db.session import engine

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès.")

if __name__ == "__main__":
    init_db()
