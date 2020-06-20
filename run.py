""" Run flat scraper """

import logging
from pathlib import Path

from main.analyzer import OfferAnalyzer
from main.scraper import OLXScraper
from utils.logging_config import get_log_config

# Define parameters for search
districts = ['Bemowo', 'Włochy', 'Wola', 'Ursynów', 'Śródmieście', 'Ochota', 'Mokotów']

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

    # Read and analyze data
    ofan = OfferAnalyzer(data_file)
    price_summary = ofan.get_price_summary()
    price_district_summary = ofan.get_price_district_summary()
    logger.info("Ending execution")
