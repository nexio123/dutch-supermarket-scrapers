from scrapers import DirkScraper, VomarScraper, DekamarktScraper
import time
import traceback

def main():
    scrapers = [
        ('Dirk', DirkScraper),
        ('Vomar', VomarScraper),
        ('Dekamarkt', DekamarktScraper)
    ]

    for name, scraper_class in scrapers:
        print(f'\nStarting {name} scraper...')
        try:
            scraper = scraper_class()
            scraper.scrape()
            scraper.save_results()
            print(f'{name} scraper completed successfully')
        except Exception as e:
            print(f'Error running {name} scraper:')
            print(traceback.format_exc())
        time.sleep(5)  # Wait between scrapers

if __name__ == '__main__':
    main()