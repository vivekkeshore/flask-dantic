import sys
from pathlib import Path

sys.path.append(Path(__file__).resolve().parent.parent.parent.as_posix())
from tests.test_main import db, User, UserModel, serialize, get_db_engine, Session, AGE

engine = get_db_engine(echo=False)
db = Session(engine)
for i in range(10000):
    user = User(username=f"user_{i}", age=AGE)
    db.add(user)


def serialize_():
    users = db.query(User).all()
    for i in users:
        _ = serialize(i, UserModel)


def serialize_many():
    users = db.query(User).all()
    _ = serialize(users, UserModel, many=True)


__benchmarks__ = [
    (serialize_, serialize_many, "Serializing many instead of one by one")
]
