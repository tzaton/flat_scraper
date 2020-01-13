import bs4
from urllib.parse import urlparse
from datetime import datetime, date, timedelta
import locale

from functions.set_locale import set_locale


class OLXAd:
    """ Flat advertisement for OLX """

    def __init__(self, ad_wrapper: bs4.element.Tag):
        self.ad_wrapper = ad_wrapper
        self.ad_params = {}

    def get_ad_params(self):
        """ Get parameters of advertisement"""
        self.ad_params['type'] = self._get_ad_type()
        self.ad_params['class'] = self._get_ad_class()
        self.ad_params['link'] = self._get_ad_link()
        self.ad_params['domain'] = self._get_ad_domain()
        self.ad_params['date'] = self._get_ad_date()
        self.ad_params['price'] = self._get_ad_price()
        self.ad_params['title'] = self._get_ad_title()

    def _get_ad_type(self):
        """ Get ad type """
        ad_type = self.ad_wrapper['rel'] or 'internal'
        return ad_type

    def _get_ad_class(self):
        """ Get ad class (promoted or not) """
        ad_class = 'promoted' if self.ad_wrapper.find('td', {'class': 'offer promoted '}) else 'standard'
        return ad_class

    def _get_ad_link(self):
        """ Get ad URL """
        ad_link = self.ad_wrapper.find('a', {'data-cy': 'listing-ad-title'})['href']
        return ad_link

    def _get_ad_domain(self):
        """ Get ad domain """
        ad_domain = urlparse(self.ad_params['link']).netloc
        return ad_domain

    def _get_ad_date(self):
        """ Get ad date added """
        ad_date = self.ad_wrapper.find('i', {'data-icon': 'clock'}).next_sibling.strip()
        if ad_date.startswith('dzisiaj'):
            ad_date_day = date.today()
        elif ad_date.startswith('wczoraj'):
            ad_date_day = date.today() - timedelta(days=1)
        else:
            with set_locale(locale.LC_ALL, 'pl_PL.UTF-8'):
                parsed_date = datetime.strptime(ad_date, '%d  %b').date()
            parsed_month = parsed_date.month
            current_month = date.today().month
            ad_year = date.today().year if current_month >= parsed_month else date.today().year - 1
            ad_date_day = parsed_date.replace(year=ad_year)
        return ad_date_day

    def _get_ad_price(self):
        """ Get ad price (total) """
        ad_price = self.ad_wrapper.find('p', {'class': 'price'}).text.strip()
        ad_price_float = float(ad_price.replace('zł', '').replace(' ', '').replace(',', '.'))
        return ad_price_float

    def _get_ad_title(self):
        """ Get ad title """
        ad_title = self.ad_wrapper.find('a', {'data-cy': 'listing-ad-title'}).text.strip()
        return ad_title


def get_ads_olx(ads_response):
    """ Get HTML for ads for OLX """
    ad_content = bs4.BeautifulSoup(ads_response.text, 'lxml').find('table', {'id': 'offers_table'})
    ad_wrappers = ad_content.find_all('tr', {'class': 'wrap'})
    return ad_wrappers


def get_offer_olx(offer_response):
    """ Get HTML for ads for OLX """
    offer_wrapper = bs4.BeautifulSoup(offer_response.text, 'lxml').find('div', {'class': 'offerdescription clr',
                                                                                'id': 'offerdescription'})
    return offer_wrapper
