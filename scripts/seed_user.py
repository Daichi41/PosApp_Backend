from app.db import SessionLocal
from app.models import User, UserRole
from app.utils.security import hash_password

with SessionLocal() as db:
    u = db.query(User).filter(User.email=="clerk@example.com").first()
    if not u:
        u = User(
            email="clerk@example.com",
            password_hash=hash_password("secret"),
            role=UserRole.CLERK,
        )
        db.add(u)
        db.commit()
        print("seeded: clerk@example.com / secret")
    else:
        print("already exists")
