from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.utils.constants import FOOD_CATEGORIES, FOOD_STATUS, PRIORITY_LEVELS

class DonationBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Food donation title")
    description: Optional[str] = Field(None, max_length=500, description="Additional details about the food")
    category: str = Field(..., description="Food category")
    quantity: int = Field(..., gt=0, description="Quantity of items")
    unit: str = Field(..., description="Unit of measurement (kg, pieces, servings, etc.)")
    expiry_date: datetime = Field(..., description="When the food expires")
    pickup_location: str = Field(..., min_length=5, description="Where to pick up the food")
    pickup_instructions: Optional[str] = Field(None, max_length=300, description="Special pickup instructions")
    dietary_info: Optional[List[str]] = Field(default=[], description="Dietary information (vegetarian, halal, etc.)")
    contact_phone: str = Field(..., description="Contact phone number")
    priority: str = Field(default="medium", description="Priority level")
    
    @validator('category')
    def validate_category(cls, v):
        if v not in FOOD_CATEGORIES:
            raise ValueError(f'Category must be one of: {", ".join(FOOD_CATEGORIES)}')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in PRIORITY_LEVELS:
            raise ValueError(f'Priority must be one of: {", ".join(PRIORITY_LEVELS)}')
        return v
    
    @validator('expiry_date')
    def validate_expiry_date(cls, v):
        if v <= datetime.now():
            raise ValueError('Expiry date must be in the future')
        return v

class DonationCreate(DonationBase):
    pass

class DonationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    quantity: Optional[int] = Field(None, gt=0)
    unit: Optional[str] = None
    expiry_date: Optional[datetime] = None
    pickup_location: Optional[str] = Field(None, min_length=5)
    pickup_instructions: Optional[str] = Field(None, max_length=300)
    dietary_info: Optional[List[str]] = None
    contact_phone: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    
    @validator('priority')
    def validate_priority(cls, v):
        if v and v not in PRIORITY_LEVELS:
            raise ValueError(f'Priority must be one of: {", ".join(PRIORITY_LEVELS)}')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in FOOD_STATUS:
            raise ValueError(f'Status must be one of: {", ".join(FOOD_STATUS)}')
        return v

class DonationResponse(DonationBase):
    id: str
    donor_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    claimed_at: Optional[datetime] = None
    claimed_by: Optional[str] = None
    
    class Config:
        from_attributes = True