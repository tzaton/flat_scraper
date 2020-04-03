""" Flat scraper """

import json
import logging
import re
from pprint import pformat
from urllib.parse import urlparse

import requests

from main.ad import OLXAd, get_ads
from main.filter import OLXFilter
from main.offer import OLXOffer, OtodomOffer, get_offer

# Logger
logger = logging.getLogger(__name__)


class Scraper:
    """ Flat scraper - parent class """

    def __init__(self, base_url):
        self.base_url = base_url
        self.domain = urlparse(self.base_url).netloc
        self.invalid_url = (fr"^{self.base_url}$",
                            fr"^{self.base_url}\?page=\d+$")  # ULRs to skip

        self.offer_data = []  # store offer parameters

    def check_url(self, url):
        """ Check if URL for list of ads is valid """
        valid_flag = 1
        for u in self.invalid_url:
            if re.search(u, url):
                valid_flag = 0
                break
            else:
                pass
        return valid_flag

    def export_data(self, data_file):
        """ Save collected offer data into .json file"""
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(self.offer_data, f, indent=4,
                      default=str, sort_keys=True)
        logger.info(f"Offer data has been saved into file: {data_file}")


class OLXScraper(Scraper):
    """ Flat scraper for OLX """
    BASE_URL = "https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/warszawa/"

    def __init__(self, filters_selected):
        super().__init__(self.BASE_URL)
        logger.info("Starting OLX Scraper")
        self.filters_selected = filters_selected
        self.filter_processor = OLXFilter(self.filters_selected)
        self.filter_processor.get_filters()
        self.ad_processor = OLXAd
        self.offer_processors = {'www.olx.pl': OLXOffer,
                                 'www.otodom.pl': OtodomOffer}

    def run(self):
        """ Run scraper """
        logger.info(
            f"Running OLX Scraper for selected filters:\n{pformat(self.filters_selected)}")
        self.filter_processor.get_url_params()

        for p in self.filter_processor.url_params:
            k = 1  # start on first page
            while True:
                pars = self.filter_processor.get_page(p, k)
                site = requests.get(self.base_url, params=pars)
                url_validflag = self.check_url(site.url)
                if url_validflag == 0:
                    break
                else:
                    logger.info(f"Scraping advertisements from: {site.url}")
                    ads = get_ads(self.domain, site)
                    for a in ads:
                        # Get ad processor
                        ad_processor = self.ad_processor(a)
                        ad_processor.get_ad_params()  # Get parameters for the advertisement
                        offer_pars = ad_processor.ad_params
                        # Access offer site
                        offer_site = requests.get(
                            ad_processor.ad_params['link'])
                        logger.info(
                            f"Scraping flat offer from: {offer_site.url}")
                        try:
                            offer_wrapper = get_offer(
                                offer_pars['domain'], offer_site)
                            offer_processor = self.offer_processors[offer_pars['domain']]
                            offer = offer_processor(offer_wrapper)
                            offer.get_offer_params()  # Get parameters for the offer
                            # Collect all found parameters
                            offer_pars.update(offer.offer_params)
                        except Exception as e:
                            pass  # Skip incorrect domains
                            logger.exception(e, exc_info=True)
                        logger.debug(offer_pars)
                        self.offer_data.append(offer_pars)
                k += 1
        logger.info(f"{len(self.offer_data)} flat offers have been browsed")
