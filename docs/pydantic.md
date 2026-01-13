# Pydantic Reference

**Official Docs:** https://docs.pydantic.dev/latest/  
**Version:** 2.x (v2.12+)

---

## Installation

```bash
pip install pydantic pydantic-settings
```

---

## Quick Start

```python
from pydantic import BaseModel, Field
from typing import Optional, List

class User(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
    tags: List[str] = []

# Validation happens on instantiation
user = User(name="John", email="john@example.com")
print(user.model_dump())  # {"name": "John", "email": "john@example.com", "age": None, "tags": []}
```

---

## Field Configuration

```python
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    price: float = Field(..., gt=0, description="Price must be positive")
    quantity: int = Field(default=1, ge=0)
    tags: List[str] = Field(default_factory=list)
```

### Field Constraints

| Constraint | Type | Description |
|------------|------|-------------|
| `min_length` | str | Minimum string length |
| `max_length` | str | Maximum string length |
| `gt` | number | Greater than |
| `ge` | number | Greater than or equal |
| `lt` | number | Less than |
| `le` | number | Less than or equal |
| `pattern` | str | Regex pattern |

---

## Validation

### Field Validators

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    email: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v.lower()
```

### Model Validators

```python
from pydantic import BaseModel, model_validator

class DateRange(BaseModel):
    start: int
    end: int
    
    @model_validator(mode='after')
    def check_range(self):
        if self.start >= self.end:
            raise ValueError('start must be less than end')
        return self
```

---

## Serialization

### To Dict/JSON

```python
user = User(name="John", email="john@example.com")

# To dictionary
data = user.model_dump()

# To JSON string
json_str = user.model_dump_json()

# Exclude fields
data = user.model_dump(exclude={'password'})

# Include only specific fields
data = user.model_dump(include={'name', 'email'})
```

### From Dict/JSON

```python
# From dict
user = User.model_validate({"name": "John", "email": "john@example.com"})

# From JSON
user = User.model_validate_json('{"name": "John", "email": "john@example.com"}')
```

---

## Union Types

```python
from typing import Union, Literal

class Reel(BaseModel):
    content_type: Literal["reel"] = "reel"
    script: str

class Tweet(BaseModel):
    content_type: Literal["tweet"] = "tweet"
    text: str

class ContentList(BaseModel):
    pieces: List[Union[Reel, Tweet]]
```

---

## Enums

```python
from enum import Enum
from pydantic import BaseModel

class ContentType(str, Enum):
    REEL = "reel"
    CAROUSEL = "image_carousel"
    TWEET = "tweet"

class Content(BaseModel):
    type: ContentType
```

---

## Settings Management

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str
    database_url: str = "sqlite:///./app.db"
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()  # Loads from environment/.env
```

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ValidationError` | Data doesn't match schema | Check field types and constraints |
| `value is not a valid X` | Type mismatch | Ensure correct data type |
| `field required` | Missing required field | Provide value or add default |
| `extra fields not permitted` | Unknown field in input | Remove field or use `extra='allow'` |

### Error Handling

```python
from pydantic import ValidationError

try:
    user = User(name=123)  # Invalid type
except ValidationError as e:
    print(e.errors())
    # [{'type': 'string_type', 'loc': ('name',), 'msg': 'Input should be a valid string'}]
```

---

## Config Options

```python
class Model(BaseModel):
    class Config:
        extra = 'forbid'        # Reject unknown fields
        str_strip_whitespace = True
        validate_default = True
        from_attributes = True  # Enable ORM mode
```

---

## FastAPI Integration

Pydantic models work directly as request/response types:

```python
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

app = FastAPI()

@app.post("/items/")
async def create_item(item: Item) -> Item:
    return item
```

---

## Related Specs

- [Data Models](../specs/data.md)
- [API Specification](../specs/api.md)
