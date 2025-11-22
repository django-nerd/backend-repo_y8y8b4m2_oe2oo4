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

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Mobile repair assistant schemas

class IssueCategory(BaseModel):
    """
    Mobile issue categories (e.g., iCloud/Activation Lock, FRP, Screen Lock)
    Collection name: "issuecategory"
    """
    key: str = Field(..., description="Unique key identifier, e.g., 'icloud', 'frp', 'screen-lock'")
    title: str = Field(..., description="Human readable title")
    description: Optional[str] = Field(None, description="Short description of the category")
    icon: Optional[str] = Field(None, description="Icon name for UI hints")

class SolutionStep(BaseModel):
    title: str
    details: str

class SolutionGuide(BaseModel):
    """
    Troubleshooting/how-to guides for mobile issues
    Collection name: "solutionguide"
    """
    title: str
    category_key: str = Field(..., description="Links to IssueCategory.key")
    devices: List[str] = Field(default_factory=list, description="Supported devices or OS versions")
    summary: Optional[str] = None
    steps: List[SolutionStep] = Field(default_factory=list)
    difficulty: Optional[str] = Field(None, description="easy | medium | hard")

class ServiceRequest(BaseModel):
    """
    User-submitted help requests
    Collection name: "servicerequest"
    """
    name: str
    email: EmailStr
    phone: Optional[str] = None
    device_model: Optional[str] = None
    issue_category: Optional[str] = None
    issue_description: Optional[str] = None
    urgent: bool = False

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
