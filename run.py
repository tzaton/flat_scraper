""" Run flat scraper """

import logging
from pathlib import Path

from main.scraper import OLXScraper
from utils.logging_config import get_log_config

# Define parameters for search
districts = ['Bemowo', 'Włochy', 'Wola', 'Ursynów', 'Śródmieście',
             'Żoliborz']

selected_filters = {'Umeblowane': 'Tak',
                    'Liczba pokoi': ('2 pokoje', '3 pokoje'),
                    'Cena do': '700000',
                    'Dzielnica': districts,
                    'Pow. od': '40'
                    }

# Run scraper
if __name__ == '__main__':

    # Logging configuration
    log_config = "logging.json"
    get_log_config(log_config)
    logger = logging.getLogger(__name__)

    # Run scraper
    scraper = OLXScraper(selected_filters)
    scraper.run()

    # Export data
    data_file = Path('.') / "data" / "scraper_data.json"
    scraper.export_data(data_file)
    flat_data = scraper.read_data(data_file)

    logger.info("Ending execution")
