from sqlalchemy import create_engine, Column, String, Integer, Index, engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    __table_args__ = (
        Index("idx_user_username", "username"),
    )

    username = Column(String(20), primary_key=True)
    age = Column(Integer)
    phone = Column(String(15), nullable=True)


def get_db_engine(echo=True, future=True):
    e: engine.Engine = create_engine(
        "sqlite:///test.db", echo=echo, future=future)
    with e.begin() as c:
        Base.metadata.create_all(bind=c)
    return e
