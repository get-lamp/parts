from pydantic import BaseModel
from typing import Optional
from uuid import UUID


# Shared properties
class CategoryBase(BaseModel):
    name: str


# Properties to receive on category creation
class CategoryCreate(CategoryBase):
    pass


# Properties to receive on category update
class CategoryUpdate(CategoryBase):
    pass


# Properties shared by models stored in DB
class CategoryInDBBase(CategoryBase):
    id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Category(CategoryInDBBase):
    pass


# Shared properties
class PartBase(BaseModel):
    uuid: UUID
    category_id: Optional[int] = None
    identifier: Optional[str] = None
    qty: Optional[int] = None
    datasheet: Optional[str] = None
    description: Optional[str] = None


# Properties to receive on part creation
class PartCreate(PartBase):
    pass


# Properties to receive on part update
class PartUpdate(PartBase):
    pass


# Properties shared by models stored in DB
class PartInDBBase(PartBase):
    id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Part(PartInDBBase):
    pass
