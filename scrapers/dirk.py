from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor
from .base import BaseScraper
import time
import re

class DirkScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.search_terms = {
            'melk': 'https://www.dirk.nl/zoeken/producten/melk',
            'brood': 'https://www.dirk.nl/zoeken/producten/brood',
            'kaas': 'https://www.dirk.nl/zoeken/producten/kaas'
        }
        # Compile regex patterns once during initialization
        self.price_pattern = re.compile(r'€\s*([0-9]+)[,.]([0-9]+)')
        self.volume_patterns = [
            re.compile(pattern) for pattern in [
                r'([0-9]+\s*(?:ml|ML|liter|Liter|L|l))',
                r'([0-9]+\s*(?:g|G|gram|Gram|kg|KG|kilo|Kilo))',
                r'([0-9]+\s*(?:stuks|Stuks|stuk|Stuk|st|ST))'
            ]
        ]
        self.unit_price_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in [
                r'€\s*[0-9,.]+\s*per\s*(?:liter|l|100g|kg|stuk)',
                r'per\s*(?:liter|l|100g|kg|stuk)\s*€\s*[0-9,.]+'
            ]
        ]

    def extract_volume_weight(self, text):
        for pattern in self.volume_patterns:
            match = pattern.search(text)
            if match:
                return match.group(1).strip()
        return None

    def extract_unit_price(self, text):
        for pattern in self.unit_price_patterns:
            match = pattern.search(text)
            if match:
                return match.group(0).strip()
        return None

    def process_product(self, container):
        try:
            product_text = container.text

            # Basic product info
            product_link = container.find_element(By.CSS_SELECTOR, 'a[aria-label="Bekijk product"]')
            product_img = container.find_element(By.CSS_SELECTOR, 'img.main-image')
            name = product_img.get_attribute('alt')
            product_url = product_link.get_attribute('href')

            # Price
            price_match = self.price_pattern.search(product_text)
            price = f'€{price_match.group(1)},{price_match.group(2)}' if price_match else 'Price not found'

            # Additional info
            volume_weight = self.extract_volume_weight(product_text)
            unit_price = self.extract_unit_price(product_text)

            # Promotions
            promotion = None
            if any(keyword in product_text.lower() for keyword in ['korting', 'aanbieding', 'actie', '2e gratis', '1+1']):
                lines = product_text.split('\n')
                promotion = next((line.strip() for line in lines 
                                if any(keyword in line.lower() 
                                    for keyword in ['korting', 'aanbieding', 'actie', '2e gratis', '1+1'])), None)

            return {
                'name': name,
                'price': price,
                'volume_weight': volume_weight,
                'unit_price': unit_price,
                'promotion': promotion,
                'url': 'https://www.dirk.nl' + product_url if product_url.startswith('/') else product_url,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            print(f'Error processing product: {str(e)}')
            return None

    def scrape_category(self, category, url):
        self.driver.get(url)
        
        # Wait for first product to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'img.main-image'))
            )
        except Exception as e:
            print(f'Timeout waiting for products to load: {str(e)}')
            return

        # Find all product containers
        product_containers = self.driver.find_elements(
            By.CSS_SELECTOR, 'div[class*="product-card"]'
        )
        print(f'Found {len(product_containers)} products in {category}')

        # Process products in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(self.process_product, product_containers))
            
        # Add successful results to products list
        for result in results:
            if result:
                result['category'] = category
                self.products.append(result)
                print(f'Added {result["name"]} - {result["price"]}')

    def scrape(self):
        print('Starting Dirk scraper...')
        
        # Handle cookie consent once at the start
        self.driver.get('https://www.dirk.nl')
        try:
            cookie_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 
                    '[data-test-id="accept-all-cookies-button"], #accept-all-button, button[class*="cookie"]'))
            )
            cookie_button.click()
        except Exception as e:
            print(f'Cookie handling error: {str(e)}')

        # Process categories
        for term, url in self.search_terms.items():
            try:
                print(f'\nProcessing category: {term}')
                self.scrape_category(term, url)
            except Exception as e:
                print(f'Error processing category {term}: {str(e)}')
