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
        print(f'Current page title: {self.driver.title}')

        # Print all elements with 'product' in their attributes
        elements = self.driver.find_elements(By.CSS_SELECTOR, '[class*="product"], [id*="product"]')
        print(f'Found {len(elements)} elements containing "product" in class or id')
        for elem in elements[:5]:  # Print first 5 as sample
            print(f'Product element found:')
            print(f'  Tag: {elem.tag_name}')
            print(f'  Class: {elem.get_attribute("class")}')
            print(f'  ID: {elem.get_attribute("id")}')
            print(f'  Text: {elem.text[:100]}...')

        # Try multiple selectors for product grid
        selectors = [
            '[data-test-id="product-grid-item"]',
            '.product-grid-item',
            '[class*="ProductCard"]',
            '[class*="product-card"]',
            '[class*="productCard"]',
            'article',
            '.grid-item'
        ]

        products_found = False
        for selector in selectors:
            try:
                products = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if products:
                    print(f'\nFound {len(products)} products with selector: {selector}')
                    print(f'Sample product HTML:')
                    print(products[0].get_attribute('outerHTML')[:500])
                    products_found = True

                    for product in products:
                        try:
                            # Get all text and divide into lines
                            product_text = product.text
                            print(f'\nRaw product text:\n{product_text}')
                            
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

                    if products_found:
                        break

            except Exception as e:
                print(f'Error with selector {selector}: {str(e)}')

        if not products_found:
            print('\nNo products found with any selector')
            # Print page source for debugging
            print('\nPage source preview:')
            print(self.driver.page_source[:1000])
