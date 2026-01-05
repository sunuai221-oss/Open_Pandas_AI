# db/test_db.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.session import get_session
from db.models import User

def main():
    with get_session() as session:
        try:
            new_user = User(username="testuser_sqlalchemy")
            session.add(new_user)
            session.commit()
            print(f"Insert OK, id={new_user.id}, username={new_user.username}")

            user = session.query(User).filter_by(username="testuser_sqlalchemy").first()
            if user:
                print(f"Read OK: id={user.id}, username={user.username}")
            else:
                print("Warning: read problem after insertion.")

            session.delete(new_user)
            session.commit()
            print("Testuser deleted (cleanup)")
        except Exception as e:
            print("Error during insert/read test:", e)
            session.rollback()

if __name__ == "__main__":
    main()
