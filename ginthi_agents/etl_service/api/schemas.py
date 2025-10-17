from pydantic import BaseModel
from typing import Optional

class ReportRequest(BaseModel):
    pass  # No specific input needed

class ReportResponse(BaseModel):
    status: str
    message: str
    reference_id: Optional[str] = None
    file_path: Optional[str] = None
    error: Optional[str] = None