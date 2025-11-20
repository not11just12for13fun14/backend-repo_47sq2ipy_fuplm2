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

# Auth/User (example retained)
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

# Core e-commerce builder schemas
class Store(BaseModel):
    """
    Merchant store configuration
    Collection: "store"
    """
    name: str = Field(..., description="Store name")
    subdomain: Optional[str] = Field(None, description="Subdomain or handle, e.g. my-shop")
    domain: Optional[str] = Field(None, description="Custom domain if configured")
    description: Optional[str] = Field(None, description="Brief description of the store")
    logo_url: Optional[str] = Field(None, description="Logo URL")
    theme: Optional[str] = Field("default", description="Selected theme identifier")
    is_published: bool = Field(False, description="Whether storefront is publicly visible")

class Product(BaseModel):
    """
    Products tied to a store
    Collection: "product"
    """
    store_id: str = Field(..., description="Owning store ID (ObjectId as string)")
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price")
    compare_at_price: Optional[float] = Field(None, ge=0, description="Original price for discounts")
    currency: str = Field("USD", description="Currency code")
    category: Optional[str] = Field(None, description="Product category")
    in_stock: bool = Field(True, description="Inventory flag")
    image_urls: List[str] = Field(default_factory=list, description="Image gallery URLs")

# Add more schemas (Collection, Order, Page, etc.) later as we expand
