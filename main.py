import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import create_document, get_documents
from schemas import ChannelProfile, ContentIdea, VideoTask

app = FastAPI(title="YouTube Shorts Automator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "YouTube Shorts Automator Backend running"}

# Simple ideation prompt helper
class IdeationRequest(BaseModel):
    niche: str
    keywords: List[str] = []
    language: str = "id"

class IdeationResponse(BaseModel):
    ideas: List[ContentIdea]

# Mock AI ideation without external dependencies
# In a real system, plug into an LLM provider.

def generate_shorts_ideas(niche: str, keywords: List[str], language: str) -> List[ContentIdea]:
    base_hashtags = [f"#{niche.replace(' ', '')}", "#shorts", "#fyp", "#viral"]
    seeds = keywords[:3] or [niche]
    suggestions: List[ContentIdea] = []
    for i, seed in enumerate(seeds, start=1):
        title = f"{seed.title()} dalam 30 Detik: Tips #{i}"
        hook = f"{seed.title()} yang jarang dibahas!"
        angle = "Listicle cepat 3 poin"
        cta = "Follow untuk tips harian!"
        description = f"Ringkasan {seed} singkat, praktis, dan mudah dipraktekkan. Simpan dan bagikan!"
        posting_time = "19:00 WIB"
        suggestions.append(ContentIdea(
            topic=seed,
            hook=hook,
            angle=angle,
            cta=cta,
            title=title,
            description=description,
            hashtags=base_hashtags + [f"#{seed.replace(' ', '')}"],
            posting_time=posting_time,
        ))
    return suggestions

@app.post("/api/ideate", response_model=IdeationResponse)
def ideate(req: IdeationRequest):
    ideas = generate_shorts_ideas(req.niche, req.keywords, req.language)
    # persist each idea
    saved_ids = []
    for idea in ideas:
        try:
            doc_id = create_document("contentidea", idea)
            saved_ids.append(doc_id)
        except Exception:
            # database may be unavailable; continue
            pass
    return {"ideas": ideas}

@app.post("/api/channel", response_model=dict)
def create_channel(profile: ChannelProfile):
    try:
        _id = create_document("channelprofile", profile)
        return {"id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ideas", response_model=List[ContentIdea])
def list_ideas(limit: int = 20):
    try:
        docs = get_documents("contentidea", {}, limit)
        # Convert Mongo docs to Pydantic-friendly dicts
        cleaned = []
        for d in docs:
            d.pop("_id", None)
            cleaned.append(ContentIdea(**d))
        return cleaned
    except Exception:
        # If DB not available, return a sample
        return generate_shorts_ideas("motivasi", ["produktif", "mindset", "bisnis"], "id")

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
        from database import db
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
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
