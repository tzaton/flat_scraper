import requests
import bs4
from urllib.parse import urlparse
from datetime import datetime, date, timedelta
import locale

from set_locale import set_locale


class Offer:
    """ Flat offer """

    def __init__(self, offer_wrapper: bs4.element.Tag):
        self.offer_wrapper = offer_wrapper

        # Ad parameters
        self.offer_type = self._get_offer_type()
        self.offer_class = self._get_offer_class()
        self.offer_link = self._get_offer_link()
        self.offer_domain = self._get_offer_domain()
        self.offer_date = self._get_offer_date()
        self.offer_page = None

        # Offer parameters
        self.offer_price = self._get_offer_price()

    def view_offer(self):
        """ Open offer URL """
        self.offer_page = requests.get(self.offer_link)

    def _get_offer_type(self):
        """ Get offer type """
        offer_type = self.offer_wrapper['rel'] or 'internal'
        return offer_type

    def _get_offer_class(self):
        """ Get offer class (promoted or not) """
        offer_class = 'promoted' if self.offer_wrapper.find('td', {'class': 'offer promoted '}) else 'standard'
        return offer_class

    def _get_offer_link(self):
        """ Get offer URL """
        offer_link = self.offer_wrapper.find('a', {'data-cy': 'listing-ad-title'})['href']
        return offer_link

    def _get_offer_domain(self):
        """ Get offer domain """
        offer_domain = urlparse(self.offer_link).netloc
        return offer_domain

    def _get_offer_price(self):
        """ Get offer price (total) """
        offer_price = self.offer_wrapper.find('p', {'class': 'price'}).text
        offer_price_int = int(offer_price.replace('zł', '').replace(' ', '').strip())
        return offer_price_int

    def _get_offer_date(self):
        """ Get offer date added """
        offer_date = self.offer_wrapper.find('i', {'data-icon': 'clock'}).next_sibling.strip()
        if offer_date.startswith('dzisiaj'):
            offer_date_day = date.today()
        elif offer_date.startswith('wczoraj'):
            offer_date_day = date.today() - timedelta(days=1)
        else:
            with set_locale(locale.LC_ALL, 'pl_PL.UTF-8'):
                parsed_date = datetime.strptime(offer_date, '%d  %b').date()
            parsed_month = parsed_date.month
            current_month = date.today().month
            offer_year = date.today().year if current_month >= parsed_month else date.today().year - 1
            offer_date_day = parsed_date.replace(year=offer_year)
        return offer_date_day

