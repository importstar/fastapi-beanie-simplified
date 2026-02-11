# FastAPI Clean Architecture Project Instructions

## 📁 Project Structure Overview

This project follows **Clean Architecture** principles with **Domain-Driven Design (DDD)** patterns using FastAPI, Beanie (MongoDB), and modular structure.

### 🏗️ Architecture Layers

```
apiapp/
├── core/                    # Business Logic & Shared Components Layer
│   ├── __init__.py
│   ├── base_repository.py   # Base repository pattern
│   ├── base_schemas.py      # Base Pydantic schemas
│   ├── base_use_case.py     # Base use case pattern
│   ├── config.py            # App configuration & settings
│   ├── exceptions.py        # Custom business exceptions
│   ├── http_error.py        # HTTP error handling
│   ├── router.py            # Base router configuration
│   ├── security.py          # JWT, password hashing
│   ├── validation_error.py  # Validation error handling
│   └── dependencies/        # Shared dependencies (auth, validation, etc.)
│       ├── __init__.py
│       └── auth.py          # Authentication dependencies
├── infrastructure/          # Infrastructure & External Services Layer
│   ├── __init__.py
│   ├── database.py          # MongoDB connection & Beanie setup
│   └── gridfs.py            # File storage
├── middlewares/             # FastAPI Middlewares
│   ├── __init__.py
│   ├── base.py              # init_all_middlewares function
│   ├── cors.py              # CORS & compression
│   ├── security.py          # User agent filtering
│   └── timing.py            # Performance timing
├── utils/                   # Utility Functions
│   ├── __init__.py
│   ├── logging.py           # Logging configuration
│   └── request_logs.py      # Request logging
├── cmd/                     # Command Line Interface Components
│   └── __init__.py
├── shares/                  # Shared Resources
└── modules/                 # Feature Modules (Clean Architecture)
    ├── __init__.py
    ├── auth/                # Authentication module
    │   ├── __init__.py
    │   └── schemas.py       # Auth schemas
    ├── user/                # User management module
    │   ├── __init__.py
    │   ├── model.py         # User database model
    │   ├── repository.py    # User data access layer
    │   ├── router.py        # User API endpoints
    │   ├── schemas.py       # User schemas
    │   └── use_case.py      # User business logic
    ├── health/              # Health check module
    │   ├── __init__.py
    │   ├── router.py        # Health check endpoints
    │   └── schemas.py       # Health check schemas
    └── examples/            # Example module (for testing)
```

## 🎯 Core Principles

### 1. **Dependency Direction**

- **Modules** depend on **Core** (import from `apiapp.core.*`)
- **Core** does NOT depend on **Modules**
- **Infrastructure** implements interfaces defined in **Core**
- **Models** are now within each module for better organization

### 2. **Module Structure**

Each feature module MUST follow this exact pattern:

```
modules/{feature}/
├── __init__.py
├── model.py        # Database Model (Beanie Document)
├── schemas.py      # Pydantic schemas (DTOs)
├── repository.py   # Data access layer
├── use_case.py     # Business logic layer (with dependency providers)
└── router.py       # API endpoints
```

### 3. **Dependency Injection Pattern**

- Use FastAPI's `Depends()` for ALL dependencies
- Create dependency providers in `core/dependencies/`
- Inject use cases, repositories, and services through dependencies
- NO direct instantiation in routers

## 📋 Coding Patterns & Guidelines

### **String Quotes Convention**

- **Use double quotes (`"`) as the primary string delimiter**
- Use single quotes (`'`) only when the string contains double quotes
- Be consistent within the same file/module

```python
# ✅ Good - Use double quotes
name = "John Doe"
message = "Welcome to our API"
sql_query = "SELECT * FROM users WHERE email = 'user@example.com'"

# ❌ Bad - Mixed quotes without reason
name = 'John Doe'
message = "Welcome to our API"
```

### **1. Model Pattern**

Each module should contain its own model file:

```python
# modules/{feature}/model.py
from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class {Model}(Document):
    """Database model for {feature}"""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: str = Field(default="active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "{feature_plural}"  # Collection name in MongoDB
        indexes = [
            "name",
            "status", 
            "created_at"
        ]
```

### **2. Use Case Pattern**

```python
# modules/{feature}/use_case.py
from fastapi import Depends
from typing import Optional

from apiapp.core.base_repository import BaseRepository
from .model import {Model}
from .repository import {Feature}Repository

class {Feature}UseCase:
    def __init__(
        self,
        {feature}_repository: {Feature}Repository,
        other_service: Optional[SomeService] = None
    ):
        self.{feature}_repository = {feature}_repository
        self.other_service = other_service

    async def {action}(self, data: {Schema}) -> {ReturnType}:
        """Business logic with validation"""
        # 1. Validate business rules
        if not self._validate_business_rules(data):
            raise ValidationError("Business rule violation")

        # 2. Process data
        processed_data = self._process_data(data)

        # 3. Call repository
        result = await self.{feature}_repository.create(processed_data)

        # 4. Return result
        return result

    def _validate_business_rules(self, data: {Schema}) -> bool:
        """Private method for business validation"""
        return True


# Dependency providers in same file
async def get_{feature}_repository() -> {Feature}Repository:
    """Get {feature} repository instance"""
    return {Feature}Repository()


async def get_{feature}_use_case(
    repository: {Feature}Repository = Depends(get_{feature}_repository)
) -> {Feature}UseCase:
    """Get {feature} use case with injected dependencies"""
    return {Feature}UseCase({feature}_repository=repository)
```

### **3. Repository Pattern**

```python
# modules/{feature}/repository.py
from apiapp.core.base_repository import BaseRepository
from .model import {Model}

class {Feature}Repository(BaseRepository[{Model}]):
    def __init__(self):
        super().__init__({Model})

    async def find_by_{field}(self, {field}: str) -> {Model} | None:
        """Custom query methods"""
        return await self.model.find_one({"{field}": {field}})

    async def find_active(self) -> List[{Model}]:
        """Find only active records"""
        return await self.model.find({"status": "active"}).to_list()
```

### **4. Router Pattern**

```python
# modules/{feature}/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from apiapp.core.dependencies import get_current_active_user, RoleChecker
from apiapp.modules.user.model import User
from .use_case import get_{feature}_use_case, {Feature}UseCase
from .schemas import {Schema}Request, {Schema}Response

router = APIRouter(prefix="/v1/{feature}", tags=["{Feature}"])

# Use "" for root endpoint, NOT "/"
@router.get("", response_model=List[{Schema}Response])
async def list_{feature}(
    current_user: User = Depends(get_current_active_user),
    {feature}_use_case: {Feature}UseCase = Depends(get_{feature}_use_case)
):
    """List all {feature} items"""
    items = await {feature}_use_case.get_all()
    return [{Schema}Response.from_entity(item) for item in items]

@router.post("", response_model={Schema}Response, status_code=status.HTTP_201_CREATED)
async def create_{feature}(
    data: {Schema}Request,
    current_user: User = Depends(get_current_active_user),
    {feature}_use_case: {Feature}UseCase = Depends(get_{feature}_use_case)
):
    """Create new {feature}"""
    try:
        item = await {feature}_use_case.create(data)
        return {Schema}Response.from_entity(item)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{item_id}", response_model={Schema}Response)
async def get_{feature}(
    item_id: str,
    current_user: User = Depends(get_current_active_user),
    {feature}_use_case: {Feature}UseCase = Depends(get_{feature}_use_case)
):
    """Get {feature} by ID"""
    item = await {feature}_use_case.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="{Feature} not found")
    return {Schema}Response.from_entity(item)
```

### **5. Cross-Module Dependencies**

When a use case needs to call another module's use case:

```python
# modules/auth/use_case.py
from fastapi import Depends

from ..user.use_case import get_user_use_case, UserUseCase
from .repository import AuthRepository

class AuthUseCase:
    def __init__(
        self,
        auth_repository: AuthRepository,
        user_use_case: UserUseCase
    ):
        self.auth_repository = auth_repository
        self.user_use_case = user_use_case

    async def login(self, credentials: LoginRequest) -> TokenResponse:
        """Login with user validation"""
        # Use another module's use case
        user = await self.user_use_case.get_by_email(credentials.email)

        # Auth-specific business logic
        if not verify_password(credentials.password, user.password):
            raise AuthenticationError("Invalid credentials")

        return await self._generate_tokens(user)


# Dependency providers
async def get_auth_repository() -> AuthRepository:
    return AuthRepository()


async def get_auth_use_case(
    auth_repository: AuthRepository = Depends(get_auth_repository),
    user_use_case: UserUseCase = Depends(get_user_use_case)
) -> AuthUseCase:
    """Get auth use case with user use case injection"""
    return AuthUseCase(
        auth_repository=auth_repository,
        user_use_case=user_use_case
    )
```

### **6. Schemas Pattern**

```python
# modules/{feature}/schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from apiapp.core.base_schemas import BaseSchema

class {Schema}Base(BaseModel):
    """Base schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class {Schema}Request({Schema}Base):
    """Request schema for creating/updating"""
    pass

class {Schema}Response({Schema}Base, BaseSchema):
    """Response schema with additional fields"""
    id: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def from_entity(cls, entity) -> "{Schema}Response":
        """Convert entity to response schema"""
        return cls(
            id=str(entity.id),
            name=entity.name,
            description=entity.description,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
```

### **7. Pagination Pattern with fastapi_pagination**

This project uses **fastapi_pagination** library with **Beanie pagination** for consistent paginated responses.

```python
# modules/{feature}/repository.py
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.beanie import paginate

from apiapp.core.base_repository import BaseRepository
from .model import {Model}

class {Feature}Repository(BaseRepository[{Model}]):
    def __init__(self):
        super().__init__({Model})

    async def get_paginated(self, params: Params) -> Page[{Model}]:
        """Get paginated results"""
        return await paginate(self.model, params)

    async def find_by_status_paginated(
        self,
        status: str,
        params: Params
    ) -> Page[{Model}]:
        """Get paginated results filtered by status"""
        query = self.model.find({"status": status})
        return await paginate(query, params)
```

```python
# modules/{feature}/use_case.py
from fastapi import Depends
from fastapi_pagination import Page, Params

from .repository import {Feature}Repository
from .schemas import {Schema}Response

class {Feature}UseCase:
    def __init__(self, {feature}_repository: {Feature}Repository):
        self.{feature}_repository = {feature}_repository

    async def get_all_paginated(self, params: Params) -> Page[{Schema}Response]:
        """Get paginated list of items"""
        page = await self.{feature}_repository.get_paginated(params)

        # Transform entities to response schemas
        items = [self._entity_to_response(item) for item in page.items]

        # Return new page with transformed items
        return Page(
            items=items,
            total=page.total,
            page=page.page,
            size=page.size,
            pages=page.pages
        )

    def _entity_to_response(self, entity) -> {Schema}Response:
        """Convert entity to response schema"""
        return {Schema}Response.from_entity(entity)
```

```python
# modules/{feature}/router.py
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params

from apiapp.core.dependencies import get_current_active_user
from apiapp.modules.user.model import User
from .use_case import get_{feature}_use_case, {Feature}UseCase
from .schemas import {Schema}Response

router = APIRouter(prefix="/v1/{feature}", tags=["{Feature}"])

@router.get("", response_model=Page[{Schema}Response])
async def list_{feature}(
    params: Params = Depends(),
    current_user: User = Depends(get_current_active_user),
    {feature}_use_case: {Feature}UseCase = Depends(get_{feature}_use_case)
):
    """Get paginated list of {feature} items"""
    return await {feature}_use_case.get_all_paginated(params)

@router.get("/by-status/{status}", response_model=Page[{Schema}Response])
async def list_{feature}_by_status(
    status: str,
    params: Params = Depends(),
    current_user: User = Depends(get_current_active_user),
    {feature}_use_case: {Feature}UseCase = Depends(get_{feature}_use_case)
):
    """Get paginated list filtered by status"""
    return await {feature}_use_case.get_by_status_paginated(status, params)
```

**Pagination Query Parameters:**

- `page`: Page number (default: 1)
- `size`: Items per page (default: 50, max: 100)

**Example API calls:**

```
GET /v1/users?page=1&size=20
GET /v1/users/by-status/active?page=2&size=10
```

**Response format:**

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8
}
```

## 🔧 Essential Patterns

### **Error Handling**

```python
# Always use specific HTTP exceptions
from fastapi import HTTPException, status

# ✅ Good
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Resource not found"
)

# ❌ Bad
raise Exception("Something went wrong")
```

### **Authentication & Authorization**

```python
# Use shared dependencies from core
from apiapp.core.dependencies import (
    get_current_active_user,
    RoleChecker
)

# Role-based access
require_admin = RoleChecker("admin")

@router.delete("/{item_id}")
async def delete_item(
    item_id: str,
    admin_user: User = Depends(require_admin)  # Only admin can delete
):
    pass
```

### **Database Operations**

```python
# Always use repository pattern
# ✅ Good
item = await self.item_repository.find_by_id(item_id)

# ❌ Bad
item = await Item.get(item_id)
```

### **Response Models**

```python
# Always specify response_model
@router.get("", response_model=List[ItemResponse])
async def list_items():
    pass

@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item():
    pass
```

## 🚫 Anti-Patterns to Avoid

1. **NO direct model imports in routers**

   ```python
   # ❌ Bad
   from apiapp.modules.user.model import User
   user = await User.find_one({"email": email})

   # ✅ Good
   user = await user_use_case.get_by_email(email)
   ```

2. **NO business logic in routers**

   ```python
   # ❌ Bad - business logic in router
   @router.post("/users")
   async def create_user(data: UserRequest):
       if len(data.password) < 8:
           raise HTTPException(400, "Password too short")
       user = User(**data.dict())
       await user.save()

   # ✅ Good - business logic in use case
   @router.post("/users")
   async def create_user(
       data: UserRequest,
       user_use_case: UserUseCase = Depends(get_user_use_case)
   ):
       return await user_use_case.create_user(data)
   ```

3. **NO cross-module imports between modules**

   ```python
   # ❌ Bad
   from apiapp.modules.user.repository import UserRepository

   # ✅ Good - Import use case dependency provider
   from ..user.use_case import get_user_use_case, UserUseCase
   ```

## 📊 File Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Router prefixes**: `/v1/{feature}` (lowercase, plural if applicable)
- **Router tags**: `["{Feature}"]` (PascalCase, singular)

## 🎯 When Creating New Features

### **Option 1: Using CLI Tools (Recommended)**

The project includes a powerful CLI module generator:

```bash
# Interactive mode - will prompt for module name and features
poetry run velo module

# Direct creation with module name
poetry run velo module create {feature_name}

# Force overwrite existing files
poetry run velo module create {feature_name} --force

# Dry run to see what files will be created
poetry run velo module create {feature_name} --dry-run

# List existing modules
poetry run velo module list
```

The CLI will automatically generate:
- `modules/{feature}/model.py` - Database model with proper Beanie Document
- `modules/{feature}/schemas.py` - Request/Response schemas
- `modules/{feature}/repository.py` - Data access layer with BaseRepository
- `modules/{feature}/use_case.py` - Business logic with dependency providers
- `modules/{feature}/router.py` - API endpoints with proper routing

### **Option 2: Manual Creation**

If creating manually:

1. **Create module directory**: `modules/{feature}/`
2. **Add `__init__.py`** to make it a Python package  
3. **Create all required files**: `model.py`, `schemas.py`, `repository.py`, `use_case.py`, `router.py`
4. **Follow the exact patterns** shown above
5. **Export router** with variable name `router`
6. **Add dependency providers** in `use_case.py` file
7. **The auto-discovery system** will automatically include your router

## 💡 Pro Tips

- Use type hints everywhere
- Add docstrings to all public methods
- Use `async/await` only for I/O operations
- Keep use cases focused on single responsibilities
- Test use cases independently with mocked repositories
- Use dependency injection for ALL external dependencies

Remember: **Consistency is key**. Follow these patterns exactly to maintain clean, maintainable, and scalable code.