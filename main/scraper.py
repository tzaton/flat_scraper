import re
from urllib.parse import urlparse
import logging
from pprint import pformat
import json
from pathlib import Path

import requests

from main.ad import OLXAd, get_ads_olx, get_offer_olx
from main.filter import OLXFilter
from main.offer import OLXOffer, OtodomOffer


class OLXScraper:
    """ Flat scraper for OLX """
    BASE_URL = "https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/warszawa/"
    DOMAIN = urlparse(BASE_URL).netloc

    INVALID_URL = (fr"^{BASE_URL}$",
                   fr"^{BASE_URL}\?page=\d+$")  # ULRs to skip

    DATA_PATH = Path(__file__).parent.parent / 'data'  # Directory to store data files

    def __init__(self, filters_selected):
        logging.info("Starting OLX Scraper")
        self.filters_selected = filters_selected
        self.filter_processor = OLXFilter(self.filters_selected)
        self.filter_processor.get_filters()
        self.ad_processor = OLXAd
        self.offer_processors = {'www.olx.pl': OLXOffer,
                                 'www.otodom.pl': OtodomOffer}
        self.offer_data = []  # store offer parameters

    def check_url(self, url):
        """ Check if URL for list of ads is valid """
        valid_flag = 1
        for u in self.INVALID_URL:
            if re.search(u, url):
                valid_flag = 0
                break
            else:
                pass
        return valid_flag

    def export_data(self, file_name):
        """ Save collected offer data into .json file"""
        data_file = self.DATA_PATH / file_name
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(self.offer_data, f, indent=4, default=str)
        logging.info(f"Offer data has been saved into file: {data_file}")

    def run(self):
        """ Run scraper """
        logging.info(f"Running OLX Scraper for selected filters:\n{pformat(self.filters_selected)}")
        self.filter_processor.get_url_params()

        offer_counter = 0  # count browsed offers
        for p in self.filter_processor.url_params:
            k = 1  # start on first page
            while True:
                pars = self.filter_processor.get_page(p, k)
                site = requests.get(self.BASE_URL, params=pars)
                url_validflag = self.check_url(site.url)
                if url_validflag == 0:
                    break
                else:
                    logging.info(f"Scraping advertisements from:{site.url}")
                    ads = get_ads_olx(site)
                    for a in ads:
                        ad_processor = self.ad_processor(a)
                        ad_processor.get_ad_params()  # Get parameters for the advertisement
                        offer_pars = ad_processor.ad_params
                        offer_site = requests.get(ad_processor.ad_params['link'])
                        logging.info(f"Scraping flat offer from:{offer_site.url}")
                        offer_wrapper = get_offer_olx(offer_site)
                        offer_processor = self.offer_processors[ad_processor.ad_params['domain']]
                        offer = offer_processor(offer_wrapper)
                        offer.get_offer_params()  # Get parameters for the offer
                        offer_pars.update(offer.offer_params)  # Collect all found parameters
                        logging.debug(offer_pars)
                        offer_counter += 1
                        self.offer_data.append(offer_pars)
                k += 1
        logging.info(f"{offer_counter} flat offers have been browsed")
