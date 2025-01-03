from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from .base import BaseScraper
import time
import json

class DirkScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.dirk.nl/aanbiedingen'

    def scrape(self):
        print('Starting Dirk scraper...')
        self.driver.get(self.base_url)
        time.sleep(5)  # Wait for page to load
        
        # Print page title to verify we're on the right page
        print(f'Page title: {self.driver.title}')
        
        # Accept cookies if present
        try:
            cookie_button = self.driver.find_element(By.CSS_SELECTOR, '#accept-all-button')
            if cookie_button:
                print('Found cookie button, clicking...')
                cookie_button.click()
                time.sleep(2)
        except Exception as e:
            print(f'Cookie handling error: {str(e)}')

        # First check for promotion blocks
        try:
            print('Looking for promotion items...')
            # Try different common promotion selectors
            selectors = [
                'div[class*="promotion"]',
                'div[class*="aanbieding"]',
                'div[class*="product"]',
                'article',  # Often used for product listings
                '.grid-item',  # Common for product grids
                '[data-component="product"]'
            ]
            
            for selector in selectors:
                items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                print(f'Found {len(items)} items with selector: {selector}')
                if items:
                    print(f'Sample item classes: {items[0].get_attribute("class")}')
                    print(f'Sample item text: {items[0].text[:200]}')

            # Try to find any elements that might contain prices
            price_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                '[class*="price"], [class*="prijs"], .bedrag, .euro')
            print(f'Found {len(price_elements)} price-like elements')
            if price_elements:
                print('Sample price texts:')
                for elem in price_elements[:3]:
                    print(f'- {elem.text}')

            # Look for product titles
            title_elements = self.driver.find_elements(By.CSS_SELECTOR,
                '[class*="title"], [class*="naam"], [class*="name"], h2, h3')
            print(f'Found {len(title_elements)} title-like elements')
            if title_elements:
                print('Sample titles:')
                for elem in title_elements[:3]:
                    print(f'- {elem.text}')

            # Try to construct product data from what we find
            if title_elements and price_elements:
                print('Attempting to pair titles with prices...')
                for title_elem in title_elements:
                    # Look for nearby price element
                    parent = title_elem.find_element(By.XPATH, '..')
                    price_elem = None
                    try:
                        price_elem = parent.find_element(By.CSS_SELECTOR,
                            '[class*="price"], [class*="prijs"], .bedrag, .euro')
                    except:
                        continue

                    if price_elem:
                        product_data = {
                            'category': 'Aanbiedingen',
                            'name': title_elem.text.strip(),
                            'price': price_elem.text.strip(),
                            'url': self.base_url,
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                        print(f'Found product: {product_data["name"]} - {product_data["price"]}')
                        self.products.append(product_data)

        except Exception as e:
            print(f'Error processing products: {str(e)}')

        if not self.products:
            print('No products found using standard methods')
            # Try to find any text that looks like a price (€ followed by numbers)
            try:
                all_elements = self.driver.find_elements(By.XPATH, '//*[contains(text(), "€")]')
                print(f'Found {len(all_elements)} elements containing €')
                for elem in all_elements:
                    print(f'Element with euro: {elem.text}')
            except Exception as e:
                print(f'Error searching for € symbols: {str(e)}')
