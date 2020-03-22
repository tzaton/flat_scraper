import logging
from pathlib import Path

from main.scraper import OLXScraper

districts = ['Bemowo', 'Włochy', 'Wola', 'Ursynów', 'Śródmieście',
             'Praga-Południe', 'Ochota', 'Mokotów', 'Bielany',
             'Żoliborz']
selected_filters = {'Umeblowane': 'Tak',
                    'Liczba pokoi': ('2 pokoje', '3 pokoje'),
                    'Cena do': '700000',
                    'Dzielnica': districts,
                    'Pow. od': '40'
                    }


if __name__ == '__main__':
    # Logging configuration
    log_file = Path(__file__).parent.parent / 'log' / 'flat_scraper.log'
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
    data_file = Path(__file__).parent.parent / 'data' / "olx_test.json"

    scraper = OLXScraper(selected_filters)
    scraper.run()
    scraper.export_data(data_file)  # Export data
