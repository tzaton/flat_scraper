import re

import requests
from bs4 import BeautifulSoup

from olx.url_filter import WebsiteFilter
from olx.get_offer import Offer


selected_filters = {
                    'Umeblowane': 'Tak',
                    'Liczba pokoi': ('2 pokoje', '3 pokoje'),
                    'Cena do': '',
                    'Dzielnica': ['Ochota']
                    }

if __name__ == '__main__':
    website_filters = WebsiteFilter(selected_filters)  # Create filter object
    website_filters.get_filters()  # Get available filters from website
    website_filters.get_url_params()  # Translate selected filters into URL params

    # Get urls
    base_url = website_filters.base_url
    for p in website_filters.url_params:
        k = 1  # start on first page
        while True:
            pars = website_filters.get_page(p, k)
            site = requests.get(base_url, params=pars)
            if site.url == base_url or re.search(fr"{base_url}\?page=\d+", site.url):  # Skip wrong pages
                break
            else:
                offer_content = BeautifulSoup(site.text, 'lxml').find('table', {'id': 'offers_table'})
                for o in offer_content.find_all('tr', {'class': 'wrap'}):
                    offer = Offer(o)
            k += 1
