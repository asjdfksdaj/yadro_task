from .db import LocalSession
from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
 
async def get_session() -> AsyncSession:
    async with LocalSession() as session:
        yield session
 
SessionType = Annotated[AsyncSession, Depends(get_session)]
