from typing import Generic, List, Optional, TypeVar, cast

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

T = TypeVar("T", bound=DeclarativeMeta)


class BaseRepository(Generic[T]):
    model: type[T]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_one(self, query: Select) -> Optional[T]:
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_all(self, query: Select) -> List[T]:
        result = await self.session.execute(query)
        return cast(List[T], result.scalars().all())

    async def add(self, instance: T) -> T:
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(self, instance: T, **kwargs) -> T:
        for k, v in kwargs.items():
            setattr(instance, k, v)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def delete(self, instance: T) -> None:
        await self.session.delete(instance)
        await self.session.flush()
