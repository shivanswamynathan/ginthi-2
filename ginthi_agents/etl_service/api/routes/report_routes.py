from fastapi import APIRouter, BackgroundTasks, HTTPException
from etl_service.api.schemas import ReportRequest, ReportResponse
from etl_service.services.browser_service import BrowserService
from etl_service.services.auth_service import AuthService
from etl_service.services.report_service import ReportService
from etl_service.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.post("/generate-grn", response_model=ReportResponse)
async def generate_grn_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """Generate Item Wise GRN Report from SupplyNote"""
    try:
        logger.info("Starting GRN report generation request...")
        background_tasks.add_task(generate_report_task)
        
        return ReportResponse(
            status="processing",
            message="Report generation started in background"
        )
    except Exception as e:
        logger.error(f"Request processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def generate_report_task():
    """Background task to generate report"""
    page = None
    try:
        logger.info("=== Starting Report Generation Task ===")
        
        # Get browser and create new page
        page = await BrowserService.new_page()
        
        # Login
        login_success = await AuthService.login(page)
        if not login_success:
            logger.error("Authentication failed")
            return
        
        # Navigate to report page
        nav_success = await ReportService.navigate_to_report(page)
        if not nav_success:
            logger.error("Navigation to report page failed")
            return
        
        # Set date range
        await ReportService.set_date_range(page)
        
        # Select all filters
        filter_success = await ReportService.select_all_filters(page)
        if not filter_success:
            logger.error("Filter selection failed")
            return
        
        # Generate report
        gen_success = await ReportService.generate_report(page)
        if not gen_success:
            logger.error("Report generation failed")
            return
        
        # Extract reference ID
        reference_id = await ReportService.extract_reference_id(page)
        if not reference_id:
            logger.error("Reference ID extraction failed")
            return
        
        # Download report
        file_path = await ReportService.download_report(page, reference_id)
        if not file_path:
            logger.error("Report download failed")
            return
        
        logger.info(f"=== Report Generation Completed Successfully ===")
        logger.info(f"Reference ID: {reference_id}")
        logger.info(f"File Path: {file_path}")
        
    except Exception as e:
        logger.error(f"Unexpected error in report generation: {str(e)}")
    finally:
        if page:
            await page.close()