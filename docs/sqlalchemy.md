# SQLAlchemy Reference

**Official Docs:** https://docs.sqlalchemy.org/en/20/  
**Version:** 2.0+

---

## Installation

```bash
pip install sqlalchemy
# For async support:
pip install aiosqlite
```

---

## Quick Start (ORM)

### Define Models

```python
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Create Engine & Session

```python
# SQLite
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# PostgreSQL
# DATABASE_URL = "postgresql://user:pass@localhost/dbname"
# engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### Create Tables

```python
Base.metadata.create_all(bind=engine)
```

---

## Common Operations

### Create

```python
db = SessionLocal()
user = User(name="John", email="john@example.com")
db.add(user)
db.commit()
db.refresh(user)  # Get the auto-generated ID
```

### Read

```python
# Get by ID
user = db.query(User).filter(User.id == 1).first()

# Get all
users = db.query(User).all()

# With pagination
users = db.query(User).offset(0).limit(10).all()

# Filter
active_users = db.query(User).filter(User.is_active == True).all()
```

### Update

```python
user = db.query(User).filter(User.id == 1).first()
user.name = "Jane"
db.commit()
```

### Delete

```python
db.query(User).filter(User.id == 1).delete()
db.commit()
```

---

## FastAPI Integration

```python
from fastapi import Depends
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

---

## Column Types

| SQLAlchemy Type | Python Type | Notes |
|-----------------|-------------|-------|
| `Integer` | `int` | Auto-increment with `primary_key=True` |
| `String(n)` | `str` | Max length n |
| `Text` | `str` | Unlimited length |
| `Boolean` | `bool` | |
| `Float` | `float` | |
| `DateTime` | `datetime` | |
| `JSON` | `dict` | Native JSON (PostgreSQL) |

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `OperationalError: database is locked` | SQLite concurrent writes | Use `check_same_thread=False` or switch to PostgreSQL |
| `IntegrityError: UNIQUE constraint` | Duplicate unique value | Check for existing before insert |
| `DetachedInstanceError` | Accessing lazy-loaded after session close | Use `db.refresh(obj)` or eager loading |
| `InvalidRequestError: rollback` | Transaction in invalid state | Call `db.rollback()` before retrying |

---

## Transaction Safety

```python
try:
    db.add(new_record)
    db.commit()
except Exception as e:
    db.rollback()
    raise
finally:
    db.close()
```

---

## Migration to PostgreSQL

1. Install driver:
   ```bash
   pip install psycopg2-binary
   ```

2. Update connection string:
   ```python
   DATABASE_URL = "postgresql://user:password@localhost:5432/dbname"
   ```

3. Remove SQLite-specific args:
   ```python
   engine = create_engine(DATABASE_URL)  # No connect_args
   ```

---

## Related Specs

- [Data Models](../specs/data.md)
- [Stack Decisions](../specs/stack.md)
