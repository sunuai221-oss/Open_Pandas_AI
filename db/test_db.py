# db/test_db.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.session import get_session
from db.models import User

def main():
    with get_session() as session:
        try:
            nouvel_user = User(username="testuser_sqlalchemy")
            session.add(nouvel_user)
            session.commit()
            print(f"Insertion OK, id={nouvel_user.id}, username={nouvel_user.username}")

            user = session.query(User).filter_by(username="testuser_sqlalchemy").first()
            if user:
                print(f"Lecture OK : id={user.id}, username={user.username}")
            else:
                print("Attention : probleme de lecture apres insertion.")

            session.delete(nouvel_user)
            session.commit()
            print("Testuser supprime (cleanup)")
        except Exception as e:
            print("Erreur lors du test d'insertion/lecture :", e)
            session.rollback()

if __name__ == "__main__":
    main()
