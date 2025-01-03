from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base import BaseScraper
import time

class DirkScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.dirk.nl/zoeken/producten/melk'

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

                # Get price components
                price_container = product.find_element(By.CSS_SELECTOR, '.price-container')
                try:
                    # Check for regular price
                    euros = price_container.find_element(By.CSS_SELECTOR, '.price-large').text
                    try:
                        cents = price_container.find_element(By.CSS_SELECTOR, '.price-small').text
                        price = f'€{euros},{cents}'
                    except:
                        price = f'€{euros},00'
                except:
                    price = 'Price not found'

                # Check for promotional price
                try:
                    promo_label = price_container.find_element(By.CSS_SELECTOR, '.price-label')
                    if promo_label:
                        regular_price = promo_label.find_element(By.CSS_SELECTOR, '.regular-price').text
                        promo = f'ACTIE - Normaal {regular_price}'
                    else:
                        promo = None
                except:
                    promo = None

                product_data = {
                    'name': name,
                    'price': price,
                    'quantity': quantity,
                    'promotion': promo,
                    'url': product_url,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }

                self.products.append(product_data)
                print(f'Added product: {name} - {price} - {quantity}')

            except Exception as e:
                print(f'Error extracting product data: {str(e)}')
                continue

if __name__ == '__main__':
    scraper = DirkScraper()
    scraper.scrape()
    scraper.save_results()