"""
Pet use case - business logic and data access
Simplified pattern using Beanie's built-in methods directly
"""

from .model import Pet
from .schemas import CreatePet, UpdatePet, PetResponse
from ...core.base_use_case import BaseUseCase


class PetUseCase(BaseUseCase[Pet, CreatePet, UpdatePet, PetResponse]):
    """
    Pet use case handling both business logic and data access.
    Inherits common CRUD operations from BaseUseCase.
    """

    model = Pet
    response_schema = PetResponse

    # Add custom business logic here if needed
    # For example:
    # async def get_by_name(self, name: str) -> Optional[PetResponse]:
    #     """Custom query for finding pet by name"""
    #     pet = await Pet.find_one({"name": name})
    #     return self._to_response(pet) if pet else None


# Dependency injection
def get_pet_use_case() -> PetUseCase:
    """Get PetUseCase instance"""
    return PetUseCase()
