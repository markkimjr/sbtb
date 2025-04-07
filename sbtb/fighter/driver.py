from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from sbtb.core.logging import logger


class ChromeDriver:
    @staticmethod
    def _get_options(headless=True) -> Options:
        options = Options()
        logger.info(f"driver headless mode: {headless}")
        options.add_argument("--headless=new")
        if not headless:
            options.headless = False
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-infobars")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        return options

    def get_driver(self) -> webdriver.Chrome:
        logger.info(f"------------------- Loading chrome driver ------------------")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self._get_options())
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                      get: () => undefined
                    });
                    Object.defineProperty(navigator, 'languages', {
                      get: () => ['en-US', 'en']
                    });
                    Object.defineProperty(navigator, 'platform', {
                      get: () => 'Win32'
                    });
                    Object.defineProperty(navigator, 'plugins', {
                      get: () => [1, 2, 3]
                    });
                """
            },
        )
        return driver
