import logging
from pathlib import Path

from main.scraper import OLXScraper


selected_filters = {'Umeblowane': 'Tak',
                    'Liczba pokoi': ('2 pokoje', '3 pokoje'),
                    'Cena do': '700000',
                    'Dzielnica': ['Ochota', 'Mokotów'],
                    'Pow. od': '40'
                    }


if __name__ == '__main__':
    # Logging configuration
    log_file = Path(__file__).parent.parent / 'log' / 'flat_scraper.log'
    log_formatter = logging.Formatter(fmt='%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
    sh = logging.StreamHandler()
    fh = logging.FileHandler(filename=log_file, mode='w')
    sh.setFormatter(log_formatter)
    fh.setFormatter(log_formatter)
    logging.basicConfig(level=logging.DEBUG,
                        handlers=[sh, fh])
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # Run scraper
    scraper = OLXScraper(selected_filters)
    scraper.run()
    scraper.export_data("olx_test.json")
