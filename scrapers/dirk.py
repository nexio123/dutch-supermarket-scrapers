from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from .base import BaseScraper
import time

class DirkScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.dirk.nl/zoeken/producten'
        self.search_terms = [
            'melk',
            'brood',
            'kaas',
            'groente',
            'fruit',
            'vlees',
            'kip',
            'vis',
            'drinken',
            'snack'
        ]

    def scrape(self):
        print('Starting Dirk scraper...')
        self.driver.get(self.base_url)
        time.sleep(5)  # Wait for page to load
        
        print(f'Current URL: {self.driver.current_url}')
        print(f'Page title: {self.driver.title}')
        
        # Accept cookies if present
        try:
            cookie_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                '#accept-all-button, button[data-test-id="accept-all-cookies-button"]')
            if cookie_buttons:
                print(f'Found {len(cookie_buttons)} cookie buttons')
                cookie_buttons[0].click()
                time.sleep(2)
        except Exception as e:
            print(f'Cookie handling error: {str(e)}')

        # Try to find search box with different selectors
        search_selectors = [
            'input[type="search"]',
            'input[placeholder*="zoek"]',
            'input[placeholder*="Zoek"]',
            'input[name="search"]',
            'input[aria-label*="zoek"]',
            'input[aria-label*="Zoek"]',
            '#search-input',
            '[data-test-id="search-input"]'
        ]
        
        # Print all input elements for debugging
        print('\nListing all input elements:')
        inputs = self.driver.find_elements(By.TAG_NAME, 'input')
        for i, inp in enumerate(inputs):
            try:
                print(f'Input {i}:')
                print(f'  Type: {inp.get_attribute("type")}')
                print(f'  Name: {inp.get_attribute("name")}')
                print(f'  ID: {inp.get_attribute("id")}')
                print(f'  Class: {inp.get_attribute("class")}')
                print(f'  Placeholder: {inp.get_attribute("placeholder")}')
            except:
                print(f'  Error getting input {i} attributes')

        # Try each search selector
        search_box = None
        for selector in search_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f'Found {len(elements)} elements with selector: {selector}')
                    search_box = elements[0]
                    break
            except Exception as e:
                print(f'Error with selector {selector}: {str(e)}')

        if not search_box:
            print('Could not find search box with any selector')
            return

        # Process each search term
        for term in self.search_terms:
            try:
                print(f'\nSearching for: {term}')
                # Clear and fill search box
                search_box.clear()
                time.sleep(1)
                search_box.send_keys(term)
                time.sleep(1)
                search_box.send_keys(Keys.RETURN)
                time.sleep(3)

                # Wait for results and extract products
                product_selectors = [
                    '[data-testid="product-card"]',
                    '[class*="product-card"]',
                    '[class*="product-item"]',
                    'article'
                ]

                products_found = False
                for selector in product_selectors:
                    try:
                        products = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if products:
                            print(f'Found {len(products)} products with selector: {selector}')
                            products_found = True
                            
                            for product in products:
                                try:
                                    product_text = product.text
                                    print(f'Product text: {product_text[:100]}...')
                                    
                                    # Try to extract price and name from text
                                    lines = product_text.split('\n')
                                    product_data = {
                                        'category': term,
                                        'name': lines[0] if lines else 'Unknown',
                                        'price': next((l for l in lines if '€' in l), 'Unknown'),
                                        'url': self.driver.current_url,
                                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                                    }
                                    
                                    self.products.append(product_data)
                                    print(f'Added product: {product_data["name"]} - {product_data["price"]}')
                                    
                                except Exception as e:
                                    print(f'Error extracting product data: {str(e)}')
                                    continue
                            
                            if products_found:
                                break
                    except Exception as e:
                        print(f'Error with product selector {selector}: {str(e)}')

                if not products_found:
                    print('No products found with any selector')

            except Exception as e:
                print(f'Error processing search term {term}: {str(e)}')
