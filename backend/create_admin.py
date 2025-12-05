# backend/create_admin.py
from app.db import SessionLocal
from app.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin(email, password):
    db = SessionLocal()
    try:
        hashed = pwd_context.hash(password)
        u = User(email=email, hashed_password=hashed, is_admin=True)
        db.add(u)
        db.commit()
        print("Admin created:", email)
    finally:
        db.close()

if __name__ == "__main__":
    create_admin("admin@example.com", "AdminPass123")
