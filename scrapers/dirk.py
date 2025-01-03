from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
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

    def extract_volume_weight(self, text):
        # Common Dutch volume/weight patterns
        patterns = [
            r'([0-9]+\s*(?:ml|ML|liter|Liter|L|l))',  # For volumes
            r'([0-9]+\s*(?:g|G|gram|Gram|kg|KG|kilo|Kilo))',  # For weights
            r'([0-9]+\s*(?:stuks|Stuks|stuk|Stuk|st|ST))'  # For pieces
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None

    def extract_unit_price(self, text):
        # Match patterns like "€1.99 per liter" or "€2.50 per 100g"
        patterns = [
            r'€\s*[0-9,.]+\s*per\s*(?:liter|l|100g|kg|stuk)',
            r'per\s*(?:liter|l|100g|kg|stuk)\s*€\s*[0-9,.]+'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        return None

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
            return

        # Find all product containers
        product_containers = self.driver.find_elements(
            By.CSS_SELECTOR, 'div[class*="product-card"]'
        )
        print(f'Found {len(product_containers)} product containers')

        for container in product_containers:
            try:
                # Get the complete text content of the product container
                product_text = container.text
                print(f'\nRaw product text:\n{product_text}')

                # Get product name and URL
                product_link = container.find_element(By.CSS_SELECTOR, 'a[aria-label="Bekijk product"]')
                product_img = container.find_element(By.CSS_SELECTOR, 'img.main-image')
                name = product_img.get_attribute('alt')
                product_url = product_link.get_attribute('href')

                # Extract price using regex
                price_match = re.search(r'€\s*([0-9]+)[,.]([0-9]+)', product_text)
                if price_match:
                    euros = price_match.group(1)
                    cents = price_match.group(2)
                    price = f'€{euros},{cents}'
                else:
                    price = 'Price not found'

                # Extract volume/weight
                volume_weight = self.extract_volume_weight(product_text)
                
                # Extract unit price
                unit_price = self.extract_unit_price(product_text)

                # Look for promotions
                promotion = None
                promo_keywords = ['korting', 'aanbieding', 'actie', '2e gratis', '1+1']
                for line in product_text.split('\n'):
                    if any(keyword in line.lower() for keyword in promo_keywords):
                        promotion = line.strip()
                        break

                product_data = {
                    'category': category,
                    'name': name,
                    'price': price,
                    'volume_weight': volume_weight,
                    'unit_price': unit_price,
                    'promotion': promotion,
                    'url': 'https://www.dirk.nl' + product_url if product_url.startswith('/') else product_url,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }

                self.products.append(product_data)
                print('Added product:')
                print(f'  Name: {name}')
                print(f'  Price: {price}')
                if volume_weight:
                    print(f'  Volume/Weight: {volume_weight}')
                if unit_price:
                    print(f'  Unit price: {unit_price}')
                if promotion:
                    print(f'  Promotion: {promotion}')

            except Exception as e:
                print(f'Error extracting product data: {str(e)}')
                continue
