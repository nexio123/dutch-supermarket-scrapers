from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import BaseScraper
import time

class DirkScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.dirk.nl/zoeken/producten/melk'

    def get_price(self, price_container):
        """Extract price from container, handling different formats"""
        try:
            # Try euros first
            try:
                euros = price_container.find_element(By.CSS_SELECTOR, '.hasEuros.price-large').text
                cents = price_container.find_element(By.CSS_SELECTOR, '.price-small').text
                return f'€{euros},{cents}'
            except:
                # Cents only
                cents = price_container.find_element(By.CSS_SELECTOR, '.price-large').text
                return f'€0,{cents}'
        except:
            return None

    def process_product(self, product):
        """Process a single product element"""
        try:
            # Basic info with fast selectors
            name = product.find_element(By.CSS_SELECTOR, 'img.main-image').get_attribute('alt')
            url = product.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            quantity = product.find_element(By.CSS_SELECTOR, '.subtitle').text

            # Price processing
            price_container = product.find_element(By.CSS_SELECTOR, '.price-container')
            price = self.get_price(price_container)

            # Promotion check - only if we see price-label
            promo = None
            if price_container.find_elements(By.CSS_SELECTOR, '.price-label'):
                regular = price_container.find_element(By.CSS_SELECTOR, '.regular-price').text
                regular = regular.replace('van ', '')
                promo = f'ACTIE - Normaal {regular}'

            return {
                'name': name,
                'price': price if price else 'Price not found',
                'quantity': quantity,
                'promotion': promo,
                'url': url,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            print(f'Error processing product: {str(e)}')
            return None

    def scrape(self):
        print('Starting Dirk scraper...')
        
        # Load page and wait for products
        self.driver.get(self.base_url)
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'article'))
            )
        except TimeoutException:
            print('Timeout waiting for products to load')
            return

        # Get all products at once
        products = self.driver.find_elements(By.CSS_SELECTOR, 'article')
        print(f'Found {len(products)} products')

        # Process products in parallel
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_product = {executor.submit(self.process_product, product): product 
                               for product in products}
            
            for future in as_completed(future_to_product):
                result = future.result()
                if result:
                    self.products.append(result)
                    print(f'Added product: {result["name"]} - {result["price"]} - {result["quantity"]}')
                    if result["promotion"]:
                        print(f'  Promotion: {result["promotion"]}')

if __name__ == '__main__':
    scraper = DirkScraper()
    scraper.scrape()
    scraper.save_results()