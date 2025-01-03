from abc import ABC, abstractmethod
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import os

class BaseScraper(ABC):
    def __init__(self):
        self.setup_driver()
        self.products = []

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--lang=nl')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)

    @abstractmethod
    def scrape(self):
        pass

    def save_results(self, filename=None):
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'output/{self.__class__.__name__}_{timestamp}.csv'

        os.makedirs('output', exist_ok=True)
        df = pd.DataFrame(self.products)
        df.to_csv(filename, index=False)
        print(f'Saved {len(self.products)} products to {filename}')

    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()