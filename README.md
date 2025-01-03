# Dutch Supermarket Scrapers

Web scrapers for various Dutch supermarkets including:
- Dirk
- Vomar
- Dekamarkt

## Features

- Scrapes product information including:
  - Product name
  - Price
  - Unit price
  - Category
  - Promotions (if available)
  - Product URL
- Automatic handling of cookie consent
- Infinite scroll support
- Error handling and retry logic
- CSV output with timestamps

## Requirements

- Python 3.8 or higher
- Chrome browser installed
- Required Python packages (see requirements.txt)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/nexio123/dutch-supermarket-scrapers.git
cd dutch-supermarket-scrapers
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

You can run individual scrapers:

```bash
python -m scrapers.dirk
python -m scrapers.vomar
python -m scrapers.dekamarkt
```

Or run all scrapers at once:

```bash
python main.py
```

Scraped data will be saved in the `output` directory as CSV files with timestamps.

## Output Format

The scrapers generate CSV files with the following columns:
- category: Product category
- name: Product name
- price: Current price
- unit: Unit price (price per kg/liter etc)
- url: Product page URL
- promotion: Promotional text (if available)
- timestamp: When the data was scraped

## Error Handling

The scrapers include error handling for common issues:
- Network timeouts
- Missing elements
- Rate limiting
- Dynamic content loading

Errors are logged to the console with traceback information.

## Rate Limiting

To be respectful to the websites:
- Delays between requests
- Random intervals between actions
- Maximum retries per request

## Legal Notice

Before using these scrapers, please:
1. Check the terms of service of each website
2. Respect robots.txt
3. Use reasonable request rates
4. Verify if you need permission

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License
