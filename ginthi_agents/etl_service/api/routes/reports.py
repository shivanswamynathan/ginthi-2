import datetime
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from etl_service.schemas.report import ReportRequest
from etl_service.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])

report_service = ReportService()

@router.post("/generate-grn-report")
async def generate_grn_report(request: ReportRequest):
    try:
        file_path = report_service.generate_report(request)
        if file_path:
            return {
                "status": "success",
                "message": "Report generated and downloaded",
                "file_path": file_path,
                "reference_id": file_path.split('/')[-1].split('.')[0],  # Approximate
                "generated_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate or download report")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))