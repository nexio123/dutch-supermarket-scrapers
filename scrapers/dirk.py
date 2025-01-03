from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base import BaseScraper
import time

class DirkScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.dirk.nl/boodschappen'

    def scrape(self):
        print('Starting Dirk scraper...')
        self.driver.get(self.base_url)
        time.sleep(5)  # Wait for page to load
        
        # Accept cookies if present
        try:
            cookie_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[data-test-id="accept-all-cookies-button"]')
            if cookie_buttons:
                cookie_buttons[0].click()
                time.sleep(2)
        except Exception as e:
            print(f'Cookie handling error: {str(e)}')

        # Get category links
        try:
            category_links = self.driver.find_elements(By.CSS_SELECTOR, '[data-test-id="category-overview-group"] a')
            categories = [(link.text, link.get_attribute('href')) for link in category_links if link.get_attribute('href')]
            print(f'Found {len(categories)} categories')
        except Exception as e:
            print(f'Error getting categories: {str(e)}')
            categories = []

        for category_name, category_url in categories:
            try:
                print(f'Scraping category: {category_name}')
                self.scrape_category(category_name, category_url)
            except Exception as e:
                print(f'Error scraping category {category_name}: {str(e)}')

    def scrape_category(self, category_name, category_url):
        self.driver.get(category_url)
        time.sleep(3)  # Allow dynamic content to load

        # Scroll to load all products
        last_height = self.driver.execute_script('return document.body.scrollHeight')
        while True:
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(2)
            new_height = self.driver.execute_script('return document.body.scrollHeight')
            if new_height == last_height:
                break
            last_height = new_height

        # Extract product information
        try:
            products = self.driver.find_elements(By.CSS_SELECTOR, '[data-test-id="product-card"]')
            print(f'Found {len(products)} products in {category_name}')
            
            for product in products:
                try:
                    # Basic product info
                    name_element = product.find_element(By.CSS_SELECTOR, '[data-test-id="product-card-name"]')
                    price_element = product.find_element(By.CSS_SELECTOR, '[data-test-id="product-card-price"]')
                    
                    product_data = {
                        'category': category_name,
                        'name': name_element.text if name_element else 'Unknown',
                        'price': price_element.text if price_element else 'Unknown',
                        'url': product.find_element(By.CSS_SELECTOR, 'a').get_attribute('href'),
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Try to get unit price
                    try:
                        unit_price = product.find_element(By.CSS_SELECTOR, '[data-test-id="product-card-unit-price"]')
                        product_data['unit'] = unit_price.text
                    except:
                        product_data['unit'] = None

                    # Try to get promotion
                    try:
                        promotion = product.find_element(By.CSS_SELECTOR, '[data-test-id="product-card-promotion"]')
                        product_data['promotion'] = promotion.text
                    except:
                        product_data['promotion'] = None

                    self.products.append(product_data)
                except Exception as e:
                    print(f'Error extracting product data: {str(e)}')
                    continue

        except Exception as e:
            print(f'Error finding products in category {category_name}: {str(e)}')
