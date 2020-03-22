import logging
from pathlib import Path

from main.scraper import OLXScraper

# Define parameters for search
districts = ['Bemowo', 'Włochy', 'Wola', 'Ursynów', 'Śródmieście',
             'Żoliborz']

selected_filters = {'Umeblowane': 'Tak',
                    'Liczba pokoi': ('2 pokoje', '3 pokoje'),
                    'Cena do': '500000',
                    'Dzielnica': districts,
                    'Pow. od': '40'
                    }

# Run scraper
if __name__ == '__main__':

    # Logging configuration
    log_file = Path(__file__).parent / 'log' / 'flat_scraper.log'
    log_formatter = logging.Formatter(
        fmt='%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    sh = logging.StreamHandler()
    fh = logging.FileHandler(filename=log_file,
                             mode='w',
                             encoding='utf-8')
    sh.setFormatter(log_formatter)
    fh.setFormatter(log_formatter)
    logging.basicConfig(level=logging.DEBUG,
                        handlers=[sh, fh])
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # Run scraper
    data_file = Path(__file__).parent / 'data' / "olx_test.json"

    scraper = OLXScraper(selected_filters)
    scraper.run()
    scraper.export_data(data_file)  # Export data
