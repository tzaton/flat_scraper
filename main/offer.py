import re

import bs4
import requests


def get_offer(domain: str, offer_response: requests.models.Response):
    """ Get HTML for offer """
    if domain == 'www.olx.pl':
        offer_wrapper = bs4.BeautifulSoup(offer_response.text, 'lxml').find(
            'div', {'class': 'offerdescription clr',
                    'id': 'offerdescription'})
    elif domain == 'www.otodom.pl':
        offer_wrapper = bs4.BeautifulSoup(
            offer_response.text, 'lxml').find('article')
    else:
        raise ValueError('Incorrect domain name')
    return offer_wrapper


class Offer:
    """ Flat offer - parent class """

    def __init__(self, offer_wrapper: bs4.element.Tag):
        self.offer_wrapper = offer_wrapper
        self.offer_params = {}

    def get_offer_params(self):
        """ Get parameters of offer if found """
        if self._get_offer_price_meter():
            self.offer_params['price_meter'] = self._get_offer_price_meter()
        if self._get_offer_area():
            self.offer_params['area'] = self._get_offer_area()
        if self._get_offer_furniture():
            self.offer_params['furniture'] = self._get_offer_furniture()
        if self._get_offer_owner():
            self.offer_params['owner'] = self._get_offer_owner()
        if self._get_offer_floor():
            self.offer_params['floor'] = self._get_offer_floor()
        if self._get_offer_nrooms():
            self.offer_params['nrooms'] = self._get_offer_nrooms()
        if self._get_offer_market():
            self.offer_params['market'] = self._get_offer_market()
        if self._get_offer_buildtype():
            self.offer_params['building_type'] = self._get_offer_buildtype()

    # Methods overwritten by child class
    def _get_offer_price_meter(self):
        pass

    def _get_offer_area(self):
        pass

    def _get_offer_furniture(self):
        pass

    def _get_offer_owner(self):
        pass

    def _get_offer_floor(self):
        pass

    def _get_offer_nrooms(self):
        pass

    def _get_offer_market(self):
        pass

    def _get_offer_buildtype(self):
        pass


class OLXOffer(Offer):
    """ Flat offer for OLX """

    def __init__(self, offer_wrapper):
        super().__init__(offer_wrapper)

    def _get_param_value(self, par_name):
        """ Find parameter by name """
        try:
            par_value = self.offer_wrapper.find(
                'th', text=par_name).find_next_sibling().text.strip()
        except AttributeError:
            par_value = None
        return par_value

    def _get_offer_price_meter(self):
        """ Get price per square meter """
        offer_price_meter = self._get_param_value(
            'Cena za m\u00B2')
        offer_price_meter_float = float(
            re.sub(r'[^\d\.]', '', offer_price_meter))
        return offer_price_meter_float

    def _get_offer_area(self):
        """ Get area """
        offer_area = self._get_param_value('Powierzchnia')
        offer_area_float = float(
            re.sub(r'[^\d\.]', '', offer_area.replace(',', '.')))
        return offer_area_float

    def _get_offer_furniture(self):
        """ Get flag for furniture """
        offer_furniture = self._get_param_value('Umeblowane')
        offer_furniture_flag = 1 if offer_furniture == 'Yes' else 'No'
        return offer_furniture_flag

    def _get_offer_owner(self):
        """ Get offer owner (private/business) """
        offer_owner = self._get_param_value('Oferta od')
        offer_owner_encoded = 'Private' if offer_owner == 'Osoby prywatnej' else 'Business'
        return offer_owner_encoded

    def _get_offer_floor(self):
        """ Get offer floor number """
        offer_floor = self._get_param_value('Poziom')
        if offer_floor == 'Suterena':
            offer_floor_encoded = '-1'
        elif offer_floor == 'Partner':
            offer_floor_encoded = '0'
        elif offer_floor == 'Powyżej 10':
            offer_floor_encoded = '>10'
        else:
            offer_floor_encoded = offer_floor
        return offer_floor_encoded

    def _get_offer_nrooms(self):
        """ Get offer number of rooms """
        nrooms = self._get_param_value('Liczba pokoi')
        if nrooms == '1 pokój':
            nrooms_encoded = '1'
        elif nrooms == '2 pokoje':
            nrooms_encoded = '2'
        elif nrooms == '3 pokoje':
            nrooms_encoded = '3'
        elif nrooms == '4 i więcej':
            nrooms_encoded = '>3'
        else:
            nrooms_encoded = nrooms
        return nrooms_encoded

    def _get_offer_market(self):
        """ Get offer market (primary/secondary) """
        market = self._get_param_value('Rynek')
        market_encoded = 'Primary' if market == 'Pierwotny' else 'Secondary'
        return market_encoded

    def _get_offer_buildtype(self):
        """ Get offer building type """
        building_type = self._get_param_value('Rodzaj zabudowy')
        if building_type == 'Blok':
            building_type_encoded = 'Block'
        elif building_type == 'Kamienica':
            building_type_encoded = 'Tenement'
        elif building_type == 'Apartamentowiec':
            building_type_encoded = 'Apartment'
        elif building_type == 'Pozostałe':
            building_type_encoded = 'Other'
        else:
            building_type_encoded = building_type
        return building_type_encoded


class OtodomOffer(Offer):
    """ Flat offer for Otodom """

    def __init__(self, offer_wrapper):
        super().__init__(offer_wrapper)

    def _get_offer_price_meter(self):
        """ Get price per square meter """
        offer_price_meter = self.offer_wrapper.find_all(
            lambda tag: tag.name == 'div' and re.search(
                re.compile('z\u0142/m'), tag.text))[-1].text
        offer_price_meter_float = float(
            re.sub(r'[^\d\.]', '', offer_price_meter))
        return offer_price_meter_float

    def _get_param_value(self, par_name):
        """ Find parameter by name """
        param_table = self.offer_wrapper.find(
            'section', {'class': 'section-overview'})  # Table with parameters
        par_pattern = re.compile(fr'{par_name}')
        par_value = param_table.find(
            lambda tag: tag.name == 'li' and re.search(
                par_pattern, tag.text)).text
        return par_value

    def _get_offer_area(self):
        """ Get area """
        offer_area = self._get_param_value('Powierzchnia')
        offer_area_float = float(
            re.sub(r'[^\d\.]', '', offer_area.replace(',', '.')))
        return offer_area_float

    def _get_offer_market(self):
        """ Get offer market (primary/secondary) """
        market = self._get_param_value('Rynek')
        market_encoded = 'Primary' if 'pierwotny' in market else 'Secondary'
        return market_encoded

    def _get_offer_nrooms(self):
        """ Get offer number of rooms """
        nrooms = self._get_param_value('Liczba pokoi')
        nrooms_encoded = re.sub(r'[^\d\.]', '', nrooms)
        return nrooms_encoded
