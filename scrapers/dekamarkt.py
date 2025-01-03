from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base import BaseScraper
import time

class DekamarktScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.dekamarkt.nl/producten'

    def scrape(self):
        self.driver.get(self.base_url)
        
        # Accept cookies if present
        try:
            cookie_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'cookieAccept'))
            )
            cookie_button.click()
        except:
            pass

        # Get category links
        category_links = self.driver.find_elements(By.CSS_SELECTOR, '.category-overview a')
        categories = [(link.text, link.get_attribute('href')) for link in category_links]

        for category_name, category_url in categories:
            try:
                self.scrape_category(category_name, category_url)
            except Exception as e:
                print(f'Error scraping category {category_name}: {str(e)}')

    def scrape_category(self, category_name, category_url):
        self.driver.get(category_url)
        time.sleep(2)

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
        products = self.driver.find_elements(By.CSS_SELECTOR, '.product-grid-item')
        for product in products:
            try:
                product_data = {
                    'category': category_name,
                    'name': product.find_element(By.CSS_SELECTOR, '.product-name').text,
                    'price': product.find_element(By.CSS_SELECTOR, '.product-price').text,
                    'unit': product.find_element(By.CSS_SELECTOR, '.unit-price').text,
                    'url': product.find_element(By.CSS_SELECTOR, 'a').get_attribute('href'),
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                try:
                    promotion = product.find_element(By.CSS_SELECTOR, '.promotion-badge')
                    product_data['promotion'] = promotion.text
                except:
                    product_data['promotion'] = None

                self.products.append(product_data)
            except Exception as e:
                print(f'Error extracting product data: {str(e)}')

        print(f'Scraped {len(products)} products from category {category_name}')