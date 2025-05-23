from .db import LocalSession
from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session():
    async with LocalSession() as session:
        yield session

Session = Annotated[AsyncSession, Depends(get_db_session)]