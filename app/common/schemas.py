from typing import Generic, List, TypeVar

from pydantic.v1.generics import GenericModel

T = TypeVar("T")


class PaginatedResponse(GenericModel, Generic[T]):
    items: List[T]
    total: int
    limit: int
    offset: int
