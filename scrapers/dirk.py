from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from .base import BaseScraper
import time

class DirkScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        # Define search terms and their direct URLs
        self.search_terms = {
            'melk': 'https://www.dirk.nl/zoeken/producten/melk',
            'brood': 'https://www.dirk.nl/zoeken/producten/brood',
            'kaas': 'https://www.dirk.nl/zoeken/producten/kaas',
            'groente': 'https://www.dirk.nl/zoeken/producten/groente',
            'fruit': 'https://www.dirk.nl/zoeken/producten/fruit',
            'vlees': 'https://www.dirk.nl/zoeken/producten/vlees',
            'kip': 'https://www.dirk.nl/zoeken/producten/kip',
            'vis': 'https://www.dirk.nl/zoeken/producten/vis',
            'drinken': 'https://www.dirk.nl/zoeken/producten/drinken',
            'snack': 'https://www.dirk.nl/zoeken/producten/snack'
        }

    def scrape(self):
        print('Starting Dirk scraper...')
        
        # Handle cookie consent once at the start
        self.driver.get('https://www.dirk.nl')
        time.sleep(3)
        try:
            cookie_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                '[data-test-id="accept-all-cookies-button"], #accept-all-button')
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
                time.sleep(2)  # Wait between categories
            except Exception as e:
                print(f'Error processing category {term}: {str(e)}')

    def scrape_category(self, category, url):
        self.driver.get(url)
        time.sleep(5)  # Wait for page to load
        
        print(f'Scraping URL: {url}')
        
        # Scroll to load all products
        last_height = self.driver.execute_script('return document.body.scrollHeight')
        while True:
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(2)
            new_height = self.driver.execute_script('return document.body.scrollHeight')
            if new_height == last_height:
                break
            last_height = new_height

        # Look for product cards
        try:
            products = self.driver.find_elements(By.CSS_SELECTOR, 
                '[data-test-id="product-grid-item"], .product-grid-item, [class*="ProductCard"]')
            print(f'Found {len(products)} products')

            for product in products:
                try:
                    # Get all text and divide into lines
                    product_text = product.text
                    lines = [l.strip() for l in product_text.split('\n') if l.strip()]
                    
                    if lines:  # Only process if we have some text
                        product_data = {
                            'category': category,
                            'name': lines[0],  # First line is usually the name
                            'price': next((l for l in lines if '€' in l), 'Unknown'),
                            'url': url,
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        # Try to get unit price
                        unit_price = next((l for l in lines if 'per' in l.lower()), None)
                        if unit_price:
                            product_data['unit'] = unit_price
                        
                        # Try to get promotion
                        promo = next((l for l in lines if any(w in l.lower() for w in ['korting', 'aanbieding', 'actie'])), None)
                        if promo:
                            product_data['promotion'] = promo

                        self.products.append(product_data)
                        print(f'Added product: {product_data["name"]} - {product_data["price"]}')

                except Exception as e:
                    print(f'Error extracting product data: {str(e)}')
                    continue

        except Exception as e:
            print(f'Error finding products: {str(e)}')
