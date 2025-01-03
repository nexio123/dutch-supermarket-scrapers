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
            # Get all text content first
            product_text = container.text
            print(f'\nProcessing product text: {product_text}')

            # Basic product info
            product_link = container.find_element(By.CSS_SELECTOR, 'a[aria-label="Bekijk product"]')
            product_img = product_link.find_element(By.CSS_SELECTOR, 'img.main-image')
            name = product_img.get_attribute('alt')
            product_url = product_link.get_attribute('href')

            # Find price container and get euros/cents separately
            try:
                price_container = container.find_element(By.CSS_SELECTOR, '.price-container')
                euros = price_container.find_element(By.CSS_SELECTOR, '.price-large').text
                cents = price_container.find_element(By.CSS_SELECTOR, '.price-small').text
                price = f'€{euros},{cents}'
            except:
                # Fallback to regex if we can't find the elements
                price_match = self.price_pattern.search(product_text)
                price = f'€{price_match.group(1)},{price_match.group(2)}' if price_match else 'Price not found'

            # Additional info
            volume_weight = self.extract_volume_weight(product_text)
            unit_price = self.extract_unit_price(product_text)

            # Promotions
            promotion = None
            promo_keywords = ['korting', 'aanbieding', 'actie', '2e gratis', '1+1']
            for line in product_text.split('\n'):
                if any(keyword in line.lower() for keyword in promo_keywords):
                    promotion = line.strip()
                    break

            result = {
                'name': name,
                'price': price,
                'volume_weight': volume_weight,
                'unit_price': unit_price,
                'promotion': promotion,
                'url': 'https://www.dirk.nl' + product_url if product_url.startswith('/') else product_url,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            print(f'Successfully processed {name} - {price}')
            return result

        except Exception as e:
            print(f'Error processing product: {str(e)}')
            return None

    def scrape_category(self, category, url):
        self.driver.get(url)
        time.sleep(3)  # Wait for dynamic content to load
        
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
            By.CSS_SELECTOR, '[class*="product-card"], [class*="ProductCard"]'
        )
        print(f'Found {len(product_containers)} products in {category}')
        
        # Print first container for debugging
        if product_containers:
            print(f'First container HTML: {product_containers[0].get_attribute("outerHTML")}')

        # Process products
        for container in product_containers:
            result = self.process_product(container)
            if result:
                result['category'] = category
                self.products.append(result)

    def scrape(self):
        print('Starting Dirk scraper...')
        
        # Handle cookie consent once at the start
        self.driver.get('https://www.dirk.nl')
        time.sleep(3)  # Wait for cookie popup
        
        try:
            cookie_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                'button[data-test-id="accept-all-cookies-button"], #accept-all-button, [class*="cookie"] button')
            
            if cookie_buttons:
                print(f'Found {len(cookie_buttons)} cookie buttons')
                for button in cookie_buttons:
                    try:
                        if 'accept' in button.text.lower() or 'accepteer' in button.text.lower():
                            print(f'Clicking cookie button with text: {button.text}')
                            button.click()
                            time.sleep(1)
                            break
                    except:
                        continue
        except Exception as e:
            print(f'Cookie handling error: {str(e)}')

        # Just scrape melk for testing
        try:
            print('\nProcessing category: melk')
            self.scrape_category('melk', 'https://www.dirk.nl/zoeken/producten/melk')
        except Exception as e:
            print(f'Error processing category: {str(e)}')

        # Save results
        self.save_results()

if __name__ == '__main__':
    scraper = DirkScraper()
    scraper.scrape()
