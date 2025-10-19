# seed_user.py (Backend 直下)
from sqlalchemy import select
from app.models import User
from app.utils.security import hash_password
from app.db import SessionLocal  # Alembicでテーブル作成済みを前提にする

EMAIL = "clerk@example.com"
PASSWORD = "secret"

def main() -> None:
    with SessionLocal() as s:
        user = s.execute(select(User).where(User.email == EMAIL)).scalar_one_or_none()
        if user:
            print(f"skip: {EMAIL} already exists (id={user.id})")
            return
        s.add(User(email=EMAIL, password_hash=hash_password(PASSWORD)))
        s.commit()
        print(f"created: {EMAIL} / {PASSWORD}")

if __name__ == "__main__":
    main()
