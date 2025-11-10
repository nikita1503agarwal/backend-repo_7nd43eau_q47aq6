"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class ChannelProfile(BaseModel):
    name: str = Field(..., description="Channel name")
    niche: str = Field(..., description="Primary niche or theme")
    target_audience: Optional[str] = Field(None, description="Who is the channel for")
    keywords: List[str] = Field(default_factory=list, description="Seed keywords for ideation")
    language: str = Field("id", description="Language code, e.g., 'id' for Indonesian, 'en' for English")

class ContentIdea(BaseModel):
    channel_id: Optional[str] = Field(None, description="Reference to channel profile id")
    topic: str = Field(..., description="Short core topic")
    hook: str = Field(..., description="Opening hook line")
    angle: str = Field(..., description="Unique angle or format")
    cta: str = Field(..., description="Call to action")
    title: str = Field(..., description="SEO friendly title")
    description: str = Field(..., description="Description optimized for search")
    hashtags: List[str] = Field(default_factory=list, description="Hashtags for discoverability")
    posting_time: str = Field(..., description="Suggested posting time")

class VideoTask(BaseModel):
    idea_id: Optional[str] = Field(None, description="Reference to content idea id")
    status: str = Field("planned", description="planned | scripting | editing | scheduled | published")
    notes: Optional[str] = Field(None)

# Example schemas kept for reference
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
