import os
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from etl_service.config import config
from etl_service.schemas.report import ReportRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.wait = None
        self.download_dir = Path(config.DOWNLOAD_DIR)
        self.download_dir.mkdir(exist_ok=True)

    def _setup_driver(self) -> None:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Remove for debugging
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        prefs = {
            "download.default_directory": str(self.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def login(self) -> bool:
        if not self.driver:
            self._setup_driver()
        
        try:
            self.driver.get(f"{config.SUPPLYNOTE_BASE_URL}/signin")
        
            username_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))  # Adjust selector if needed
            #password_field = self.driver.find_element(By.NAME, "password") 
            print("uername field", username_field)
            #print("password field", password_field) # Adjust
            #username_field.send_keys(config.SUPPLYNOTE_USERNAME)
            #password_field.send_keys(config.SUPPLYNOTE_PASSWORD)
            
            #submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")  # Adjust
            #submit_btn.click()
            
            # Wait for redirect or dashboard
            self.wait.until(EC.url_contains("/dashboard"))  # Assume dashboard URL
            logger.info("Login successful")
            return True
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    def generate_report(self, request: ReportRequest) -> Optional[str]:
        if not self.login():
            return None
        
        try:
            self.driver.get(f"{config.SUPPLYNOTE_BASE_URL}/reports/itemwise-grn-report/")
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))  # Wait for form
            
            # Location
            location_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "location"))))  # Adjust ID/class
            location_select.select_by_visible_text(request.location)
            
            # Date Range - assuming datetime-local inputs
            start_input = self.driver.find_element(By.ID, "start_date")  # Adjust
            end_input = self.driver.find_element(By.ID, "end_date")
            start_input.clear()
            end_input.clear()
            start_input.send_keys(request.start_date.strftime("%m/%d/%Y %I:%M %p"))  # Format from screenshot
            end_input.send_keys(request.end_date.strftime("%m/%d/%Y %I:%M %p"))
            
            # States (multi-select)
            if request.states:
                states_select = Select(self.driver.find_element(By.ID, "states"))
                for state in request.states:
                    states_select.select_by_visible_text(state)
            
            # Cities
            if request.cities:
                cities_select = Select(self.driver.find_element(By.ID, "cities"))
                for city in request.cities:
                    cities_select.select_by_visible_text(city)
            
            # InterStock / IntraStock toggles (assuming checkboxes)
            if request.inter_stock:
                self.driver.find_element(By.ID, "interstock").click()
            if request.intra_stock:
                self.driver.find_element(By.ID, "intrastock").click()
            
            # Suppliers (multi)
            if request.suppliers:
                suppliers_select = Select(self.driver.find_element(By.ID, "suppliers"))
                for supp in request.suppliers:
                    suppliers_select.select_by_visible_text(supp)
            
            # Products, Categories, Subcategories - similar multi-selects
            if request.products:
                products_select = Select(self.driver.find_element(By.ID, "products"))
                for prod in request.products:
                    products_select.select_by_visible_text(prod)
            if request.categories:
                cats_select = Select(self.driver.find_element(By.ID, "categories"))
                for cat in request.categories:
                    cats_select.select_by_visible_text(cat)
            if request.subcategories:
                subcats_select = Select(self.driver.find_element(By.ID, "subcategories"))
                for sub in request.subcategories:
                    subcats_select.select_by_visible_text(sub)
            
            # Columns - assuming it's a multi-select or toggle, skip or add if specified
            
            # Send on Email
            if request.send_email:
                email_cb = self.driver.find_element(By.ID, "send_email")
                email_cb.click()
            
            # Generate Report
            generate_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-primary:contains('Generate Report')")))
            generate_btn.click()
            logger.info("Report generation triggered")
            
            return self._wait_and_download()
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()

    def _wait_and_download(self, wait_time: int = 600) -> Optional[str]:
        start_time = time.time()
        while time.time() - start_time < wait_time:
            try:
                # Refresh or wait for history table update
                self.driver.refresh()
                time.sleep(30)  # Poll every 30s
                
                # Find first row in history table
                rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
                if rows:
                    first_row = rows[0]
                    ref_id = first_row.find_element(By.CSS_SELECTOR, "td:first-child").text.strip()  # Reference No
                    if ref_id:  # Assume it's the new one if just generated
                        download_btn = first_row.find_element(By.CSS_SELECTOR, "button:contains('Download')")
                        download_btn.click()
                        
                        # Wait for download (monitor file in dir)
                        time.sleep(10)
                        files = list(self.download_dir.glob("*.xlsx")) + list(self.download_dir.glob("*.csv"))  # Adjust extensions
                        if files:
                            latest_file = max(files, key=os.path.getctime)
                            logger.info(f"Downloaded: {latest_file}")
                            return str(latest_file)
            except Exception as e:
                logger.warning(f"Poll error: {e}")
                time.sleep(30)
        
        logger.error("Timeout waiting for report")
        return None

    def close(self):
        if self.driver:
            self.driver.quit()