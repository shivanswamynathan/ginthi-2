import asyncio
from datetime import datetime
from playwright.async_api import Page
from etl_service.config import settings
from etl_service.utils.logger import get_logger

logger = get_logger(__name__)

class ReportService:
    REPORT_PAGE = f"{settings.SUPPLYNOTE_BASE_URL}/reports/itemwise-grn-report/"
    
    @staticmethod
    async def navigate_to_report(page: Page) -> bool:
        try:
            logger.info(f"Navigating to report page: {ReportService.REPORT_PAGE}")
            await page.goto(ReportService.REPORT_PAGE, wait_until="networkidle", timeout=30000)
            logger.info("Report page loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {str(e)}")
            return False
    
    @staticmethod
    async def set_date_range(page: Page) -> bool:
        try:
            logger.info("Setting date range...")
            today = datetime.now().strftime("%m/%d/%Y")
            
            # Set start date
            start_date_input = await page.query_selector('input[placeholder*="01/10/2025"]')
            if start_date_input:
                await start_date_input.click()
                await start_date_input.triple_click()
                await start_date_input.type(f"{today} 12:00 AM", delay=50)
                logger.info(f"Start date set: {today} 12:00 AM")
            
            # Set end date
            end_date_inputs = await page.query_selector_all('input[type="text"]')
            if len(end_date_inputs) >= 2:
                await end_date_inputs[1].click()
                await end_date_inputs[1].triple_click()
                await end_date_inputs[1].type(f"{today} 12:00 PM", delay=50)
                logger.info(f"End date set: {today} 12:00 PM")
            
            return True
        except Exception as e:
            logger.error(f"Date range setting failed: {str(e)}")
            return False
    
    @staticmethod
    async def select_all_filters(page: Page) -> bool:
        try:
            logger.info("Starting filter selection...")
            
            # Select all States
            logger.info("Selecting all States...")
            await ReportService._select_dropdown_all(page, "Select States")
            
            # Select all Cities
            logger.info("Selecting all Cities...")
            await ReportService._select_dropdown_all(page, "Select Cities")
            
            # Select all Suppliers
            logger.info("Selecting all Suppliers...")
            await ReportService._select_dropdown_all(page, "Select Supplier")
            
            # Select all Products
            logger.info("Selecting all Products...")
            await ReportService._select_dropdown_all(page, "Select Products")
            
            # Select all Categories
            logger.info("Selecting all Categories...")
            await ReportService._select_dropdown_all(page, "Select Categories")
            
            # Select all Sub-Categories
            logger.info("Selecting all Sub-Categories...")
            await ReportService._select_dropdown_all(page, "Select Sub Categories")
            
            # Click InterStock button
            logger.info("Ensuring InterStock is enabled...")
            await page.click("button:has-text('InterStock')")
            await asyncio.sleep(0.3)
            
            # Click IntraStock button
            logger.info("Ensuring IntraStock is enabled...")
            await page.click("button:has-text('IntraStock')")
            await asyncio.sleep(0.3)
            
            # Ensure "Send Report on Email" is unchecked
            logger.info("Unchecking 'Send Report on Email'...")
            email_checkbox = await page.query_selector('input[type="checkbox"]')
            if email_checkbox and await email_checkbox.is_checked():
                await email_checkbox.click()
            
            logger.info("Filter selection completed successfully")
            return True
        except Exception as e:
            logger.error(f"Filter selection failed: {str(e)}")
            return False
    
    @staticmethod
    async def _select_dropdown_all(page: Page, placeholder_text: str) -> bool:
        try:
            # Click dropdown
            dropdown = await page.query_selector(f'select[placeholder*="{placeholder_text}"]')
            if dropdown:
                await dropdown.click()
                await asyncio.sleep(0.3)
                
                # Get all options and select them
                options = await page.query_selector_all(f'select[placeholder*="{placeholder_text}"] option')
                for option in options[1:]:  # Skip placeholder
                    await option.click()
                    await asyncio.sleep(0.1)
            
            return True
        except Exception as e:
            logger.warning(f"Dropdown selection failed for {placeholder_text}: {str(e)}")
            return False
    
    @staticmethod
    async def generate_report(page: Page) -> bool:
        try:
            logger.info("Clicking 'Generate Report' button...")
            await page.click('button:has-text("Generate Report")')
            
            logger.info(f"Waiting {settings.REPORT_WAIT_TIME} seconds for report generation...")
            await asyncio.sleep(settings.REPORT_WAIT_TIME)
            
            logger.info("Report generation completed")
            return True
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            return False
    
    @staticmethod
    async def extract_reference_id(page: Page) -> str:
        try:
            logger.info("Extracting reference ID from Report History...")
            
            # Get first row reference ID
            ref_id_cell = await page.query_selector('table tbody tr:first-child td:nth-child(2)')
            if ref_id_cell:
                reference_id = await ref_id_cell.text_content()
                reference_id = reference_id.strip()
                logger.info(f"Reference ID extracted: {reference_id}")
                return reference_id
            
            logger.warning("Could not extract reference ID")
            return None
        except Exception as e:
            logger.error(f"Reference ID extraction failed: {str(e)}")
            return None
    
    @staticmethod
    async def download_report(page: Page, reference_id: str) -> str:
        try:
            logger.info(f"Downloading report with reference ID: {reference_id}")
            
            # Click download button for the first row
            async with page.expect_download() as download_info:
                await page.click('button:has-text("Download")')
            
            download = await download_info.value
            
            # Save file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = settings.DOWNLOADS_DIR / f"{reference_id}_{timestamp}.xlsx"
            await download.save_as(str(file_path))
            
            logger.info(f"Report downloaded successfully: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Report download failed: {str(e)}")
            return None