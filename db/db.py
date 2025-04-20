import uuid

from decouple import config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Field, select

# Create an async engine
engine = create_async_engine(config('DATABASE_URL'), echo=config('APP_LOG_LEVEL') == 'debug')
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


async def init_db():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)


class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    token: str = Field(unique=True)
    email: str = Field(unique=True)


async def create_user(email: str) -> str:
    async with async_session() as session:
        token = str(uuid.uuid4())
        async with session.begin():
            user = User(token=token, email=email)
            session.add(user)

            return token


async def is_valid_token(token: str) -> bool:
    if token == config('K6_TEST_TOKEN'):
        return True

    async with async_session() as session:
        statement = select(User).where(User.token == token)
        result = await session.execute(statement)
        user = result.scalars().first()

        return user is not None
