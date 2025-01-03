from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from .base import BaseScraper
import time

class DirkScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.search_terms = {
            'melk': 'https://www.dirk.nl/zoeken/producten/melk',
            'brood': 'https://www.dirk.nl/zoeken/producten/brood',
            'kaas': 'https://www.dirk.nl/zoeken/producten/kaas'
        }

    def scrape(self):
        print('Starting Dirk scraper...')
        
        # Handle cookie consent once at the start
        self.driver.get('https://www.dirk.nl')
        time.sleep(3)
        try:
            cookie_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                '[data-test-id="accept-all-cookies-button"], #accept-all-button, button[class*="cookie"]')
            if cookie_buttons:
                print('Found cookie button, clicking...')
                cookie_buttons[0].click()
                time.sleep(2)
        except Exception as e:
            print(f'Cookie handling error: {str(e)}')

        # Process each search term
        for term, url in self.search_terms.items():
            try:
                print(f'\nProcessing category: {term}')
                self.scrape_category(term, url)
                time.sleep(2)
            except Exception as e:
                print(f'Error processing category {term}: {str(e)}')

    def scrape_category(self, category, url):
        self.driver.get(url)
        time.sleep(5)
        
        print(f'Scraping URL: {url}')

        # Find all product links (these contain the product names and URLs)
        product_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[aria-label="Bekijk product"]')
        print(f'Found {len(product_links)} product links')

        for link in product_links:
            try:
                # Get the product container (parent element)
                product_container = link.find_element(By.XPATH, '..')
                
                # Get product name from image alt text
                product_img = link.find_element(By.CSS_SELECTOR, 'img.main-image')
                name = product_img.get_attribute('alt')
                product_url = link.get_attribute('href')

                # Find the price container
                price_container = product_container.find_element(By.CSS_SELECTOR, '.price-container')
                
                # Get euros and cents
                euros = price_container.find_element(By.CSS_SELECTOR, '.price-large').text
                cents = price_container.find_element(By.CSS_SELECTOR, '.price-small').text
                
                # Combine into full price
                price = f'€{euros},{cents}'

                # Try to get unit price if available
                unit_price = None
                try:
                    unit_price_elem = product_container.find_element(By.CSS_SELECTOR, '[class*="unit-price"]')
                    unit_price = unit_price_elem.text
                except:
                    pass

                # Try to get promotion if available
                promotion = None
                try:
                    promo_elem = product_container.find_element(By.CSS_SELECTOR, '[class*="promotion"]')
                    promotion = promo_elem.text
                except:
                    pass

                product_data = {
                    'category': category,
                    'name': name,
                    'price': price,
                    'unit_price': unit_price,
                    'promotion': promotion,
                    'url': 'https://www.dirk.nl' + product_url if product_url.startswith('/') else product_url,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }

                self.products.append(product_data)
                print(f'Added product: {name} - {price}')

            except Exception as e:
                print(f'Error extracting product data: {str(e)}')
                continue
