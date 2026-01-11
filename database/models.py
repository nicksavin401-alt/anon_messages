from sqlalchemy import BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

engine = create_async_engine(url="sqlite+aiosqlite:///database/db.sqlite3", echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # id в TG

class Blacklist(Base):
    __tablename__ = "blacklist"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  
    owner_id: Mapped[int] = mapped_column(BigInteger)
    blocked_user_id: Mapped[int] = mapped_column(BigInteger)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
