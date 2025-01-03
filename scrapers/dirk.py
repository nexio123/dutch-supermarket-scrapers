from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base import BaseScraper
import time

class DirkScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.dirk.nl/aanbiedingen'

    def scrape(self):
        print('Starting Dirk scraper...')
        self.driver.get(self.base_url)
        time.sleep(5)  # Wait for page to load
        
        # Print page title to verify we're on the right page
        print(f'Page title: {self.driver.title}')
        
        # Accept cookies if present
        try:
            buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button')
            for button in buttons:
                if 'accept' in button.text.lower() or 'accepteer' in button.text.lower():
                    print(f'Found cookie button: {button.text}')
                    button.click()
                    time.sleep(2)
                    break
        except Exception as e:
            print(f'Cookie handling error: {str(e)}')

        # Get category links - first try product categories
        try:
            # Print all elements with 'category' in their attributes
            elements = self.driver.find_elements(By.CSS_SELECTOR, '*[class*="category"], *[id*="category"]')
            print(f'Found {len(elements)} elements with category in name')
            for elem in elements:
                print(f'Category element: {elem.tag_name} - {elem.get_attribute("class")} - {elem.text[:50]}...')

            # Try different selectors for categories
            category_links = self.driver.find_elements(By.CSS_SELECTOR, '.category a, [data-test-id*="category"] a, .categories a')
            if not category_links:
                # If no categories found, try getting all promotion links
                print('No categories found, trying promotions instead')
                category_links = self.driver.find_elements(By.CSS_SELECTOR, '[href*="aanbieding"]')

            categories = []
            for link in category_links:
                href = link.get_attribute('href')
                text = link.text
                if href and text:
                    categories.append((text, href))
                    print(f'Found category: {text} - {href}')

            print(f'Found {len(categories)} usable categories')

        except Exception as e:
            print(f'Error getting categories: {str(e)}')
            categories = []

        if not categories:
            # If still no categories, scrape current page as single category
            print('No categories found, scraping current page')
            try:
                self.scrape_category('Aanbiedingen', self.base_url)
            except Exception as e:
                print(f'Error scraping main page: {str(e)}')
        else:
            for category_name, category_url in categories:
                try:
                    print(f'Scraping category: {category_name}')
                    self.scrape_category(category_name, category_url)
                except Exception as e:
                    print(f'Error scraping category {category_name}: {str(e)}')

    def scrape_category(self, category_name, category_url):
        self.driver.get(category_url)
        time.sleep(3)  # Allow dynamic content to load

        # Print page content for debugging
        print(f'Scraping URL: {category_url}')
        print(f'Page title: {self.driver.title}')

        # Scroll to load all products
        last_height = self.driver.execute_script('return document.body.scrollHeight')
        while True:
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(2)
            new_height = self.driver.execute_script('return document.body.scrollHeight')
            if new_height == last_height:
                break
            last_height = new_height

        # Try multiple selectors for products
        selectors = [
            '[data-test-id="product-card"]',
            '.product-item',
            '.product',
            '[class*="product-"]',
            '[id*="product-"]'
        ]

        products_found = False
        for selector in selectors:
            try:
                products = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if products:
                    print(f'Found {len(products)} products using selector: {selector}')
                    products_found = True
                    
                    for product in products:
                        try:
                            # Try to get product details
                            product_text = product.text
                            print(f'Product text: {product_text[:100]}...')
                            
                            # Get any price-like text
                            price_elements = product.find_elements(By.CSS_SELECTOR, 
                                '[class*="price"], [id*="price"], .price, .bedrag, .korting')
                            
                            product_data = {
                                'category': category_name,
                                'name': product_text.split('\n')[0] if '\n' in product_text else product_text,
                                'price': price_elements[0].text if price_elements else 'Unknown',
                                'url': category_url,
                                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                            }

                            self.products.append(product_data)
                        except Exception as e:
                            print(f'Error extracting product data: {str(e)}')
                            continue
                    break
            except Exception as e:
                print(f'Error with selector {selector}: {str(e)}')

        if not products_found:
            print('No products found with any selector')
