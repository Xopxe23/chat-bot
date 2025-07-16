from typing import Generic, List, Optional, TypeVar, Any, Union, Type

from pydantic import BaseModel
from sqlalchemy.dialects import postgresql
from sqlalchemy import select, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta, selectinload
from sqlalchemy.sql import operators

from app.common.schemas import OrmModel

T = TypeVar("T", bound=DeclarativeMeta)
S = TypeVar("S", bound=OrmModel)


class BaseRepository(Generic[T, S]):
    model: type[T]
    schema: type[S]

    OPERATORS = {
        "eq": operators.eq,
        "gt": operators.gt,
        "gte": operators.ge,
        "lt": operators.lt,
        "lte": operators.le,
        "ne": operators.ne,
        "in": operators.in_op,
        "like": operators.like_op,
    }

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_one(
        self,
        joined: Optional[list[str]] = None,
        schema_cls: Optional[Type[BaseModel]] = None,
        **filter_by: Any,
    ) -> Any:
        query = select(self.model)
        query = self._apply_joins(query, joined)
        filters = self._build_filters(filter_by)
        query = query.filter(*filters)
        result = await self.session.execute(query)
        instance = result.scalars().one_or_none()
        if instance is None:
            raise ValueError(f"{self.model.__name__} not found with filters: {filter_by}")
        return (schema_cls or self.schema).model_validate(instance)

    async def get_list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[Union[str, list[str]]] = None,
        joined: Optional[list[str]] = None,
        schema_cls: Optional[Type[BaseModel]] = None,
        **filter_by: Any,
    ) -> List[Any]:
        query = select(self.model)
        query = self._apply_joins(query, joined)
        filters = self._build_filters(filter_by)
        query = query.filter(*filters)
        query = self._apply_ordering(query, order_by)
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        result = await self.session.execute(query)
        instances = result.scalars().all()
        return [(schema_cls or self.schema).model_validate(instance) for instance in instances]

    async def get_total_count(self, **filter_by: Any) -> int:
        filters = self._build_filters(filter_by)
        query = select(func.count()).select_from(self.model).filter(*filters)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def add(self, **data: Any) -> S:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return self.schema.model_validate(instance)

    def _build_filters(self, filter_kwargs: dict) -> list:
        conditions = []
        for key, value in filter_kwargs.items():
            if "__" in key:
                field_name, op_name = key.split("__", 1)
                if not hasattr(self.model, field_name):
                    raise ValueError(f"Invalid field: {field_name}")
                if op_name not in self.OPERATORS:
                    raise ValueError(f"Unsupported operator: {op_name}")
                column = getattr(self.model, field_name)
                op = self.OPERATORS[op_name]
                conditions.append(op(column, value))
            else:
                column = getattr(self.model, key)
                conditions.append(column == value)
        return conditions

    def _apply_joins(self, query, joined: Optional[list[str]]):
        if not joined:
            return query

        for rel_name in joined:
            if not hasattr(self.model, rel_name):
                raise ValueError(f"Invalid relationship: {rel_name}")
            attr = getattr(self.model, rel_name)
            query = query.options(selectinload(attr))

        return query

    def _apply_ordering(self, query, order_by: Union[str, list[str]]) -> Any:
        if not order_by:
            return query

        order_clauses = []
        fields = [order_by] if isinstance(order_by, str) else order_by
        for field in fields:
            field_parts = field.split()
            field_name = field_parts[0]
            direction = field_parts[1].lower() if len(field_parts) > 1 else "asc"

            if not hasattr(self.model, field_name):
                raise ValueError(f"Invalid sort field: {field_name}")
            column = getattr(self.model, field_name)

            clause = desc(column) if direction == "desc" else asc(column)
            order_clauses.append(clause)

        return query.order_by(*order_clauses)

    @staticmethod
    def _print_raw_sql(query) -> str:
        compiled = query.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True}
        )
        raw_sql = str(compiled)
        print("RAW SQL:", raw_sql)
        return raw_sql
