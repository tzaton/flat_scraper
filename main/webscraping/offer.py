""" Parsing offer pages """

import logging
import re

import bs4
import requests

logger = logging.getLogger(__name__)


def get_offer(domain: str, offer_response: requests.models.Response) -> bs4.element.Tag:
    """Get offer wrapper (HTML) from offer page

    Parameters
    ----------
    domain : str
        Domain where offer is published e.g. www.olx.pl
    offer_response : requests.models.Response
        Response from offer website

    Returns
    -------
    bs4.element.Tag
        raw offer data

    Raises
    ------
    ValueError
        if unsupported domain specified
    """
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


class Offer(object):
    """ Flat offer - parent class """

    def __init__(self, offer_wrapper: bs4.element.Tag):
        self.offer_wrapper = offer_wrapper
        self.offer_params = {}

    def get_offer_params(self):
        """ Get parameters of offer if found """
        try:
            self.offer_params['price_meter'] = self._get_offer_price_meter()
        except Exception as e:
            logger.exception(e)
            logger.error(f"Parameter `price_meter` not found")

        try:
            self.offer_params['area'] = self._get_offer_area()
        except Exception as e:
            logger.exception(e)
            logger.error(f"Parameter `area` not found")

        try:
            self.offer_params['furniture'] = self._get_offer_furniture()
        except Exception as e:
            logger.exception(e)
            logger.error(f"Parameter `furniture` not found")

        try:
            self.offer_params['owner'] = self._get_offer_owner()
        except Exception as e:
            logger.exception(e)
            logger.error(f"Parameter `owner` not found")

        try:
            self.offer_params['floor'] = self._get_offer_floor()
        except Exception as e:
            logger.exception(e)
            logger.error(f"Parameter `floor` not found")

        try:
            self.offer_params['nrooms'] = self._get_offer_nrooms()
        except Exception as e:
            logger.exception(e)
            logger.error(f"Parameter `nrooms` not found")

        try:
            self.offer_params['market'] = self._get_offer_market()
        except Exception as e:
            logger.exception(e)
            logger.error(f"Parameter `market` not found")

        try:
            self.offer_params['building_type'] = self._get_offer_buildtype()
        except Exception as e:
            logger.exception(e)
            logger.error(f"Parameter `building_type` not found")

    # Methods overwritten by child class
    def _get_offer_price_meter(self):
        return None

    def _get_offer_area(self):
        return None

    def _get_offer_furniture(self):
        return None

    def _get_offer_owner(self):
        return None

    def _get_offer_floor(self):
        return None

    def _get_offer_nrooms(self):
        return None

    def _get_offer_market(self):
        return None

    def _get_offer_buildtype(self):
        return None


class OLXOffer(Offer):
    """ Flat offer for OLX """

    def _get_param_value(self, par_name: str) -> str:
        """Find parameter value based on its name

        Parameters
        ----------
        par_name : str
            Offer parameter name

        Returns
        -------
        str
            parameter value for given offer
        """
        par_value = self.offer_wrapper.find(
            'span', class_="offer-details__name", text=par_name)\
                .find_next_sibling().text.strip()
        return par_value

    def _get_offer_price_meter(self):
        """Get price per square meter

        Returns
        -------
        float
            price per square meter
        """
        offer_price_meter = self._get_param_value(
            'Cena za m\u00B2')
        offer_price_meter_float = float(
            re.sub(r'[^\d\.]', '', offer_price_meter))
        return offer_price_meter_float

    def _get_offer_area(self):
        """Get area

        Returns
        -------
        float
            flat area (square meter)
        """
        offer_area = self._get_param_value('Powierzchnia')
        offer_area_float = float(
            re.sub(r'[^\d\.]', '', offer_area.replace(',', '.')))
        return offer_area_float

    def _get_offer_furniture(self):
        """Get flag for furniture

        Returns
        -------
        str
            Furniture flag - Yes (with) / No (without)
        """
        offer_furniture = self._get_param_value('Umeblowane')
        offer_furniture_flag = 1 if offer_furniture == 'Yes' else 'No'
        return offer_furniture_flag

    def _get_offer_owner(self):
        """Get offer owner type

        Returns
        -------
        str
            offer owner (private/business)
        """
        offer_owner = self._get_param_value('Oferta od')
        offer_owner_encoded = 'Private' if offer_owner == 'Osoby prywatnej' else 'Business'
        return offer_owner_encoded

    def _get_offer_floor(self):
        """Get floor number

        Returns
        -------
        str
            Floor number
        """
        offer_floor = self._get_param_value('Poziom')
        if offer_floor == 'Suterena':
            offer_floor_encoded = '-1'
        elif offer_floor == 'Parter':
            offer_floor_encoded = '0'
        elif offer_floor == 'Powyżej 10':
            offer_floor_encoded = '>10'
        else:
            offer_floor_encoded = offer_floor
        return offer_floor_encoded

    def _get_offer_nrooms(self):
        """Get number of rooms

        Returns
        -------
        str
            number of rooms in the flat
        """
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
        """Get market

        Returns
        -------
        str
            Market (primary/secondary)
        """
        market = self._get_param_value('Rynek')
        market_encoded = 'Primary' if market == 'Pierwotny' else 'Secondary'
        return market_encoded

    def _get_offer_buildtype(self):
        """Get building type

        Returns
        -------
        str
            building type
        """
        building_type = self._get_param_value('Rodzaj zabudowy')
        if building_type == 'Blok':
            building_type_encoded = 'Block'
        elif building_type == 'Kamienica':
            building_type_encoded = 'Tenement'
        elif building_type == 'Apartamentowiec':
            building_type_encoded = 'Apartment'
        elif building_type is not None:
            building_type_encoded = 'Other'
        else:
            building_type_encoded = building_type
        return building_type_encoded


class OtodomOffer(Offer):
    """ Flat offer for Otodom """

    def _get_offer_price_meter(self):
        """Get price per square meter

        Returns
        -------
        float
            price per square meter
        """
        offer_price_meter = self.offer_wrapper.find_all(
            lambda tag: tag.name == 'div' and re.search(
                re.compile(r'\d+ z\u0142/m'), tag.text))[-1].text
        offer_price_meter_float = float(
            re.sub(r'[^\d\.]', '', offer_price_meter))
        return offer_price_meter_float

    def _get_param_value(self, par_name: str) -> str:
        """Find parameter value based on its name

        Parameters
        ----------
        par_name : str
            Offer parameter name

        Returns
        -------
        str
            parameter value for given offer
        """
        param_table = self.offer_wrapper.find(
            'section', {'class': 'section-overview'})  # Table with parameters
        par_pattern = re.compile(fr'{par_name}')
        par_value = param_table.find(
            lambda tag: tag.name == 'li' and re.search(
                par_pattern, tag.text)).text
        par_value = re.sub(par_name, '', par_value).replace(':', '').strip()
        return par_value

    def _get_offer_area(self):
        """Get area

        Returns
        -------
        float
            flat area (square meter)
        """
        offer_area = self._get_param_value('Powierzchnia')
        offer_area_float = float(
            re.sub(r'[^\d\.]', '', offer_area.replace(',', '.')))
        return offer_area_float

    def _get_offer_market(self):
        """Get market

        Returns
        -------
        str
            Market (primary/secondary)
        """
        market = self._get_param_value('Rynek')
        market_encoded = 'Primary' if 'pierwotny' in market else 'Secondary'
        return market_encoded

    def _get_offer_nrooms(self):
        """Get number of rooms

        Returns
        -------
        str
            number of rooms in the flat
        """
        nrooms = self._get_param_value('Liczba pokoi')
        nrooms_encoded = re.sub(r'[^\d\.]', '', nrooms)
        return nrooms_encoded

    def _get_offer_floor(self):
        """Get floor number

        Returns
        -------
        str
            Floor number
        """
        floor = self._get_param_value('Piętro')
        if floor == 'parter':
            floor_encoded = '0'
        elif floor == '> 10':
            floor_encoded = '>10'
        else:
            floor_encoded = floor
        return floor_encoded

    def _get_offer_buildtype(self):
        """Get building type

        Returns
        -------
        str
            building type
        """
        building_type = self._get_param_value('Rodzaj zabudowy')
        if building_type == 'blok':
            building_type_encoded = 'Block'
        elif building_type == 'kamienica':
            building_type_encoded = 'Tenement'
        elif building_type == 'apartamentowiec':
            building_type_encoded = 'Apartment'
        elif building_type is not None:
            building_type_encoded = 'Other'
        else:
            building_type_encoded = building_type
        return building_type_encoded
