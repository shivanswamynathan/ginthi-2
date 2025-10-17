from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, field_validator, model_validator, ValidationInfo

class ReportRequest(BaseModel):
    location: str  # e.g., "GAU Olijulbar i"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    states: Optional[List[str]] = None
    cities: Optional[List[str]] = None
    inter_stock: bool = False
    intra_stock: bool = False
    suppliers: Optional[List[str]] = None
    products: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    subcategories: Optional[List[str]] = None
    send_email: bool = False

    # ✅ Assign default start_date if None
    @field_validator('start_date', mode='before')
    @classmethod
    def default_start_date(cls, v):
        if v is None:
            return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return v

    # ✅ Assign default end_date based on start_date
    @field_validator('end_date', mode='before')
    @classmethod
    def default_end_date(cls, v, info: ValidationInfo):
        if v is None:
            start_date = info.data.get('start_date')
            if start_date:
                return start_date.replace(hour=12, minute=0, second=0, microsecond=0)
            else:
                return datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        return v

    # ✅ Validate that date range <= 100 days
    @model_validator(mode='after')
    def validate_date_range(self):
        if self.start_date and self.end_date:
            if (self.end_date - self.start_date).days > 100:
                raise ValueError('Date range cannot exceed 100 days')
        return self
