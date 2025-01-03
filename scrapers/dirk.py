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
        # Common product searches to get a good coverage
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
        
        # Accept cookies if present
        try:
            cookie_button = self.driver.find_element(By.ID, 'accept-all-button')
            if cookie_button:
                print('Found cookie button, clicking...')
                cookie_button.click()
                time.sleep(2)
        except Exception as e:
            print(f'Cookie handling error: {str(e)}')

        # Process each search term
        for term in self.search_terms:
            try:
                print(f'\nSearching for: {term}')
                self.search_and_scrape(term)
            except Exception as e:
                print(f'Error processing search term {term}: {str(e)}')

    def search_and_scrape(self, search_term):
        try:
            # Find and clear the search box
            search_box = self.driver.find_element(By.CSS_SELECTOR, 'input[type="search"]')
            search_box.clear()
            time.sleep(1)
            
            # Enter search term and submit
            search_box.send_keys(search_term)
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)  # Wait for results to load

            # Scroll to load all products
            last_height = self.driver.execute_script('return document.body.scrollHeight')
            while True:
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(2)
                new_height = self.driver.execute_script('return document.body.scrollHeight')
                if new_height == last_height:
                    break
                last_height = new_height

            # Extract product information
            products = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="product-card"]')
            print(f'Found {len(products)} products for search term: {search_term}')

            for product in products:
                try:
                    # Get product name
                    name_elem = product.find_element(By.CSS_SELECTOR, '[data-testid="product-card-name"]')
                    
                    # Get price elements
                    price_elem = product.find_element(By.CSS_SELECTOR, '[data-testid="product-card-price"]')
                    
                    product_data = {
                        'category': search_term,
                        'name': name_elem.text.strip(),
                        'price': price_elem.text.strip(),
                        'url': product.find_element(By.CSS_SELECTOR, 'a').get_attribute('href'),
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }

                    # Try to get unit price if available
                    try:
                        unit_elem = product.find_element(By.CSS_SELECTOR, '[data-testid="product-card-unit-price"]')
                        product_data['unit'] = unit_elem.text.strip()
                    except:
                        product_data['unit'] = None

                    # Try to get promotion if available
                    try:
                        promo_elem = product.find_element(By.CSS_SELECTOR, '[data-testid="product-card-promotion"]')
                        product_data['promotion'] = promo_elem.text.strip()
                    except:
                        product_data['promotion'] = None

                    self.products.append(product_data)
                    print(f'Added product: {product_data["name"]} - {product_data["price"]}')

                except Exception as e:
                    print(f'Error extracting product data: {str(e)}')
                    continue

        except Exception as e:
            print(f'Error searching for term {search_term}: {str(e)}')
