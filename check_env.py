import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

print("DATABASE_URL (système) :", os.environ.get("DATABASE_URL"))
print("DATABASE_URL (.env chargé) :", os.getenv("DATABASE_URL"))
