import re
from urllib.parse import urlparse

import requests

from main.ad import OLXAd, get_ads_olx
from main.filter import OLXFilter


class OLXScraper:
    """ Flat scraper for OLX """
    BASE_URL = "https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/warszawa/"
    DOMAIN = urlparse(BASE_URL).netloc

    INVALID_URL = (fr"^{BASE_URL}$",
                   fr"^{BASE_URL}\?page=\d+$")

    def __init__(self, filters_selected):
        self.filters_selected = filters_selected
        self.filter_processor = OLXFilter(self.filters_selected)
        self.filter_processor.get_filters()
        self.ad_processor = OLXAd

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

    def run(self):
        """ Run scraper """
        self.filter_processor.get_url_params()

        for p in self.filter_processor.url_params:
            k = 1  # start on first page
            while True:
                pars = self.filter_processor.get_page(p, k)
                site = requests.get(self.BASE_URL, params=pars)
                url_validflag = self.check_url(site.url)
                if url_validflag == 0:
                    break
                else:
                    print(site.url)
                    ads = get_ads_olx(site)
                    for a in ads:
                        ad_processor = self.ad_processor(a)
                        ad_processor.get_ad_params()
                        print(ad_processor.ad_params)
                k += 1
