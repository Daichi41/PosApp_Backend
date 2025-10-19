from sqlalchemy import create_engine, text
import os
url = os.environ["DATABASE_URL"]
engine = create_engine(url, pool_pre_ping=True)
with engine.connect() as conn:
    print(conn.execute(text("SELECT VERSION()")).scalar())
