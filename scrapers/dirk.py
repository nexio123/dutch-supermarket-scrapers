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

        # Wait for products to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'img.main-image'))
            )
        except Exception as e:
            print(f'Timeout waiting for products to load: {str(e)}')

        # Find all product containers
        product_containers = self.driver.find_elements(
            By.CSS_SELECTOR, 'div[class*="product-card"]'
        )
        print(f'Found {len(product_containers)} product containers')

        for container in product_containers:
            try:
                # Get product name and URL
                product_link = container.find_element(By.CSS_SELECTOR, 'a[aria-label="Bekijk product"]')
                product_img = container.find_element(By.CSS_SELECTOR, 'img.main-image')
                name = product_img.get_attribute('alt')
                product_url = product_link.get_attribute('href')

                # Get the price text directly from the container
                price_text = container.text
                
                # Find price in the text (looking for € symbol followed by numbers)
                import re
                price_match = re.search(r'€\s*([0-9]+)[,.]([0-9]+)', price_text)
                if price_match:
                    euros = price_match.group(1)
                    cents = price_match.group(2)
                    price = f'€{euros},{cents}'
                else:
                    price = 'Price not found'

                # Try to get unit price from the text
                unit_price = None
                unit_price_match = re.search(r'per \w+\.?\s+€\s*[0-9,.]+', price_text)
                if unit_price_match:
                    unit_price = unit_price_match.group(0)

                # Try to find promotion in the text
                promotion = None
                promo_keywords = ['korting', 'aanbieding', 'actie', '2e gratis', '1+1']
                for line in price_text.split('\n'):
                    if any(keyword in line.lower() for keyword in promo_keywords):
                        promotion = line.strip()
                        break

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
                if promotion:
                    print(f'  Promotion: {promotion}')
                if unit_price:
                    print(f'  Unit price: {unit_price}')

            except Exception as e:
                print(f'Error extracting product data: {str(e)}')
                continue
