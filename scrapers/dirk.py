from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base import BaseScraper
import time

class DirkScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.dirk.nl/zoeken/producten/melk'

    def get_price(self, price_container):
        """Extract price from container, handling different formats"""
        try:
            # First check if we have euros
            try:
                euros = price_container.find_element(By.CSS_SELECTOR, '.hasEuros.price-large').text
                cents = price_container.find_element(By.CSS_SELECTOR, '.price-small').text
                return f'€{euros},{cents}'
            except:
                # No euros found, so this must be cents only
                cents = price_container.find_element(By.CSS_SELECTOR, '.price-large').text
                # Convert to decimal format (e.g., 97 -> €0,97)
                return f'€0,{cents}'
        except Exception as e:
            print(f'Error parsing price: {str(e)}')
            return None

    def scrape(self):
        print('Starting Dirk scraper...')
        self.driver.get(self.base_url)
        time.sleep(3)

        # Find all article elements (product containers)
        products = self.driver.find_elements(By.CSS_SELECTOR, 'article')
        print(f'Found {len(products)} products')

        for product in products:
            try:
                # Get product details
                name = product.find_element(By.CSS_SELECTOR, 'img.main-image').get_attribute('alt')
                product_url = product.find_element(By.CSS_SELECTOR, 'a[aria-label="Bekijk product"]').get_attribute('href')

                # Get quantity/volume
                try:
                    quantity = product.find_element(By.CSS_SELECTOR, 'span.subtitle').text
                except:
                    quantity = None

                # Get price
                price_container = product.find_element(By.CSS_SELECTOR, '.price-container')
                price = self.get_price(price_container)

                # Check for promotional price
                try:
                    promo_label = price_container.find_element(By.CSS_SELECTOR, '.price-label')
                    regular_price = promo_label.find_element(By.CSS_SELECTOR, '.regular-price').text
                    if regular_price:
                        regular_price = regular_price.replace('van ', '')
                        promo = f'ACTIE - Normaal {regular_price}'
                    else:
                        promo = None
                except:
                    promo = None

                product_data = {
                    'name': name,
                    'price': price if price else 'Price not found',
                    'quantity': quantity,
                    'promotion': promo,
                    'url': product_url,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }

                self.products.append(product_data)
                print(f'Added product: {name} - {price} - {quantity}')
                if promo:
                    print(f'  Promotion: {promo}')

            except Exception as e:
                print(f'Error extracting product data: {str(e)}')
                continue

if __name__ == '__main__':
    scraper = DirkScraper()
    scraper.scrape()
    scraper.save_results()