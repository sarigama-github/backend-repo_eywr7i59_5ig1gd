import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import create_document, get_documents, db
from schemas import Message

app = FastAPI(title="Developer Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Portfolio backend running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

# --------- Portfolio-specific endpoints ---------

class Project(BaseModel):
    title: str
    description: str
    tags: List[str] = []
    link: str | None = None
    github: str | None = None
    image: str | None = None

# For simplicity, serve a few featured projects from code
FEATURED_PROJECTS: List[Project] = [
    Project(
        title="Realtime Chat App",
        description="Socket-driven chat with rooms, presence, and message history.",
        tags=["React", "FastAPI", "WebSockets", "MongoDB"],
        link="https://example.com/chat",
        github="https://github.com/you/chat-app",
        image="/projects/chat.png"
    ),
    Project(
        title="E-commerce Starter",
        description="Headless store with product catalog, cart, and checkout.",
        tags=["Vite", "Tailwind", "FastAPI", "Stripe"],
        link="https://example.com/store",
        github="https://github.com/you/store",
        image="/projects/store.png"
    ),
    Project(
        title="AI Blog Summarizer",
        description="Summarizes articles and generates SEO snippets.",
        tags=["React", "FastAPI", "LLM"],
        link="https://example.com/ai-blog",
        github="https://github.com/you/ai-blog",
        image="/projects/ai.png"
    ),
]

@app.get("/api/projects", response_model=List[Project])
def list_projects():
    return FEATURED_PROJECTS

@app.post("/api/contact")
def submit_contact(message: Message):
    try:
        inserted_id = create_document("message", message)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
