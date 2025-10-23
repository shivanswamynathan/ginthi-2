from playwright.async_api import async_playwright, Browser, Page
from etl_service.config import settings
from etl_service.utils.logger import get_logger

logger = get_logger(__name__)

class BrowserService:
    _browser: Browser = None
    
    @classmethod
    async def get_browser(cls) -> Browser:
        if cls._browser is None:
            logger.info("Launching Playwright browser...")
            playwright = await async_playwright().start()
            cls._browser = await playwright.chromium.launch(
                headless=settings.BROWSER_HEADLESS
            )
        return cls._browser
    
    @classmethod
    async def close_browser(cls):
        if cls._browser:
            logger.info("Closing browser...")
            await cls._browser.close()
            cls._browser = None
    
    @classmethod
    async def new_page(cls) -> Page:
        browser = await cls.get_browser()
        page = await browser.new_page()
        page.set_default_timeout(settings.PAGE_TIMEOUT)
        return page