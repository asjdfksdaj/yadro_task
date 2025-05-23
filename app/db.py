from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .settings import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
LocalSession = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
