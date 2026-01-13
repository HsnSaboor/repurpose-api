# FastAPI Reference

**Official Docs:** https://fastapi.tiangolo.com/  
**Version:** Latest (0.115+)

---

## Installation

```bash
pip install fastapi uvicorn[standard]
```

---

## Quick Start

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

**Run development server:**
```bash
fastapi dev main.py
# or
uvicorn main:app --reload --host 127.0.0.1 --port 8002
```

---

## Common Patterns

### Path Parameters

```python
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

### Query Parameters

```python
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

### Request Body with Pydantic

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
async def create_item(item: Item):
    return item
```

### Dependency Injection

```python
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/")
async def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### Streaming Response (SSE)

```python
from fastapi.responses import StreamingResponse

@app.post("/stream/")
async def stream_data():
    async def generate():
        for i in range(10):
            yield f"data: {i}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

### File Upload

```python
from fastapi import File, UploadFile

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    return {"filename": file.filename, "size": len(content)}
```

### CORS Middleware

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `422 Unprocessable Entity` | Request validation failed | Check request body matches Pydantic model |
| `ModuleNotFoundError: uvicorn` | Uvicorn not installed | `pip install uvicorn[standard]` |
| `Address already in use` | Port occupied | Use different port or kill process |
| `CORS error` | Missing CORS middleware | Add CORSMiddleware (see above) |

---

## Project Config

```python
app = FastAPI(
    title="My API",
    description="API description",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc
)
```

---

## Testing

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
```

---

## Related Specs

- [API Specification](../specs/api.md)
- [Stack Decisions](../specs/stack.md)
