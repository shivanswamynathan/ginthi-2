import asyncio
from datetime import datetime
from playwright.async_api import Page
from etl_service.config import settings
from etl_service.utils.logger import get_logger

logger = get_logger(__name__)

class ReportService:
    
    @staticmethod
    async def navigate_to_report(page: Page) -> bool:
        try:
            # Step 1: Click Reports button in sidebar
            logger.info("Step 1: Clicking Reports button in sidebar...")
            await page.click('button:has-text("Reports")', force=True)
            logger.info("Reports button clicked")
            await asyncio.sleep(3)
            
            # Step 2: Click Item Wise GRN Report V2 card
            logger.info("Step 2: Clicking Item Wise GRN Report V2 card...")
            await page.click('[ui-sref="reports.itemWiseGRN"]', force=True)
            logger.info("Item Wise GRN card clicked")
            await asyncio.sleep(10)
            
            return True
            
        except Exception as e:
            logger.error(f"Navigation failed: {str(e)}")
            return False
    
    @staticmethod
    async def set_date_range(page: Page) -> bool:
        try:
            logger.info("Checking date range...")
            # Date range is already set with defaults - no changes needed
            logger.info("Date range using defaults - not modified")
            return True
        except Exception as e:
            logger.error(f"Date range check failed: {str(e)}")
            return False
    
    @staticmethod
    async def select_all_filters(page: Page) -> bool:
        try:
            logger.info("Starting filter selection...")
            await asyncio.sleep(1)
            
            # Wait for iframe to be present
            iframe_element = await page.wait_for_selector("iframe.ng-isolate-scope")
            frame = await iframe_element.content_frame()
            
            logger.info("Looking for Location dropdown (p-multiselect) inside iframe...")
            
            try:
                # Find the multiselect for outlets INSIDE IFRAME
                await frame.wait_for_selector('p-multiselect[formcontrolname="outlets"]', timeout=10000)
                
                multiselect_button = frame.locator('p-multiselect[formcontrolname="outlets"]')
                
                # Click to open dropdown
                await multiselect_button.click(force=True)
                logger.info("Location dropdown opened")
                await asyncio.sleep(2)
                
                # Click the "Select All" checkbox
                logger.info("Looking for Select All checkbox...")
                select_all_checkbox = frame.locator('div[role="checkbox"].p-checkbox-box').first
                
                await select_all_checkbox.wait_for(state="visible", timeout=10000)
                await select_all_checkbox.scroll_into_view_if_needed()
                await asyncio.sleep(1)
                
                await select_all_checkbox.click(force=True)
                logger.info("Clicked Select All checkbox - all locations selected!")
                
                await asyncio.sleep(2)
                
                # Close dropdown
                await frame.click('body', force=True)
                await asyncio.sleep(1)
                
                logger.info("Filter selection completed - all locations selected at once")
                return True
                
            except Exception as e:
                logger.warning(f"Location selection error: {str(e)}")
                return True
                
        except Exception as e:
            logger.error(f"Filter selection failed: {str(e)}")
            return False
        
        
    @staticmethod
    async def generate_report(page: Page) -> bool:
        try:
            logger.info("Looking for Generate Report button...")
            await asyncio.sleep(1)
        
            logger.info("Clicking 'Generate Report' button...")

            iframe_element = await page.wait_for_selector("iframe.ng-isolate-scope")
            frame = await iframe_element.content_frame()

            await frame.wait_for_selector("span.p-button-label",
                                timeout=180000)
           
            button =  frame.locator("span.p-button-label", has_text="Generate Report")

            

            await button.wait_for(state="visible", timeout=10000)
            await button.click()
            print("Clicked 'Generate Report' button successfully!")

            logger.info("Waiting 10 minutes for report generation...")
            await asyncio.sleep(600)  # 10 minutes
            
            logger.info("Report generation completed")
            return True
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            return False

    
    @staticmethod
    async def download_report(page: Page, reference_id: str = None) -> str:
        try:
            logger.info("Downloading report from first row...")
            
            # Wait for iframe to be present
            iframe_element = await page.wait_for_selector("iframe.ng-isolate-scope")
            frame = await iframe_element.content_frame()
            
            logger.info("Waiting for table to load...")
            # Wait for table row to load inside iframe
            await frame.wait_for_selector("table tbody tr", timeout=10000)
            await asyncio.sleep(2)
            
            logger.info("Looking for Download button...")
            # Wait for p-button-label with Download text
            await frame.wait_for_selector("span.p-button-label", timeout=10000)
            
            # Get the download button using locator (same way as Generate Report)
            download_button = frame.locator("span.p-button-label", has_text="Download").first
            
            # Wait for button to be visible
            await download_button.wait_for(state="visible", timeout=10000)
            
            logger.info("Clicking Download button...")
            async with page.expect_download() as download_info:
                await download_button.click(force=True)
            
            download = await download_info.value

            logger.info("Waiting for file to download completely...")
            await asyncio.sleep(10)
            
            
            # Save file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = settings.DOWNLOADS_DIR / f"item_wise_grn_report_{timestamp}.csv"
            await download.save_as(str(file_path))
            
            logger.info(f"Report downloaded successfully: {file_path}")
            return str(file_path)
                
        except Exception as e:
            logger.error(f"Report download failed: {str(e)}")
            return None