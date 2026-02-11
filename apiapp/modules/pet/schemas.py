"""
Pet module schemas (DTOs)
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

from ...core.base_schemas import BaseSchema


class BasePet(BaseModel):
    """Base schema with common fields for pet"""

    name: str = Field(
        ..., min_length=1, max_length=100, description="Name of the pet"
    )
    description: Optional[str] = Field(
        default=None, max_length=500, description="Description of the pet"
    )
    is_active: bool = Field(default=True, description="Indicates if the pet is active")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp",
    )


class CreatePet(BaseModel):
    """Schema for creating a new pet"""

    name: str = Field(
        ..., min_length=1, max_length=100, description="Name of the pet"
    )
    description: Optional[str] = Field(
        default=None, max_length=500, description="Description of the pet"
    )


class UpdatePet(BaseModel):
    """Schema for updating pet data - all fields optional"""

    name: Optional[str] = Field(
        default=None, min_length=1, max_length=100, description="Name of the pet"
    )
    description: Optional[str] = Field(
        default=None, max_length=500, description="Description of the pet"
    )
    is_active: Optional[bool] = Field(
        default=None, description="Indicates if the pet is active"
    )


class PetResponse(BaseSchema, BasePet):
    """Response schema for pet"""
    pass