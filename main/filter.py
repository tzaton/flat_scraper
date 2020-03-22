import re
import urllib.parse
import logging
from pprint import pformat

import requests
from bs4 import BeautifulSoup


class OLXFilter:
    """ Manage website filters for OLX """
    BASE_URL = "https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/warszawa/"
    BASE_SITE = requests.get(BASE_URL)
    BASE_CONTENT = BeautifulSoup(BASE_SITE.text, 'lxml')
    SEARCH_PATTERN = re.compile(r'search\[.+\]')  # pattern for filters

    def __init__(self, filters_selected: dict):
        self.filters = {}  # dictionary to store filter parameters
        self.filters_selected = filters_selected  # filters specified for scraping
        self.url_params = []  # filters passed to GET method (list of dicts)

    def get_filters(self):
        """ Get all filters for website """
        self.filters = self._get_filters_main()
        self.filters.update(self._get_filters_district())
        self.filters.update(self._get_filters_owner())
        self.filters.update(self._get_filters_photos())
        self.filters.update(self._get_filters_order())
        self.filters.update(self._get_filters_page())
        logging.info(
            f"Available filters for www.olx.pl are:\n{pformat(self.filters)}")

    def _get_filters_main(self):
        """ Get filters from frame """
        filters = {}
        for param in self.BASE_CONTENT.find(class_="clr multifilters subSelectActive").find_all(
                class_=re.compile("param param(Select|Float)")):
            filter_code = param['data-name']
            for filter_item in param.find_all('div', {'class': re.compile('filter-item')}):
                filter_name = filter_item.find(
                    'span', {'class': 'header block'}).text
                filter_name = filter_name.replace(
                    b'\xc2\xb2'.decode('utf-8'), '2')  # Replace square meters
                multiparam = filter_item.find(
                    'input', {'class': re.compile('defaultval')})
                if multiparam:
                    filter_code = re.search(
                        self.SEARCH_PATTERN, multiparam['class'][2]).group()
                else:
                    filter_code = filter_code.replace('[]', '[{param_order}]')
                filters[filter_name] = {'param': filter_code}

        # Assign values for parameters (collected manually)
        filters['Rodzaj zabudowy']['values'] = {'Blok': 'blok',
                                                'Kamienica': 'kamienica',
                                                'Apartamentowiec': 'apartamentowiec',
                                                'Loft': 'loft',
                                                'Pozostałe': 'pozostale'}
        filters['Rynek']['values'] = {'Pierwotny': 'primary',
                                      'Wtórny': 'secondary'}
        filters['Poziom']['values'] = {'Suterena': 'floor_-1',
                                       'Parter': 'floor_0',
                                       '1': 'floor_1',
                                       '2': 'floor_2',
                                       '3': 'floor_3',
                                       '4': 'floor_4',
                                       '5': 'floor_5',
                                       '6': 'floor_6',
                                       '7': 'floor_7',
                                       '8': 'floor_8',
                                       '9': 'floor_9',
                                       '10': 'floor_10',
                                       'Powyżej 10': 'floor_11',
                                       'Poddasze': 'floor_17'}
        filters['Umeblowane']['values'] = {'Tak': 'yes',
                                           'Nie': 'no'}
        filters['Liczba pokoi']['values'] = {'1 pokój': 'one',
                                             '2 pokoje': 'two',
                                             '3 pokoje': 'three',
                                             '4 i więcej': 'four'}
        return filters

    def _get_filters_district(self):
        """ Get district filter """
        districts = {'Dzielnica': {'param': '', 'values': {}}}
        districts['Dzielnica']['values'] = {d.text: d['href'].split('=')[-1] for d in self.BASE_CONTENT.find_all(
            'a', {'href': re.compile('district_id')})}
        districts['Dzielnica']['param'] = re.search(self.SEARCH_PATTERN,
                                                    urllib.parse.unquote(self.BASE_CONTENT.find(
                                                        'a', {'href': re.compile('district_id')})['href'])).group()
        return districts

    def _get_filters_owner(self):
        """ Get offer owner filter """
        owners = {'Właściciel': {'param': '', 'values': {}}}
        owners['Właściciel']['values'] = {[text for text in d.stripped_strings][0]: d['href'].split('=')[-1] for d in
                                          self.BASE_CONTENT.find_all('a', class_='fleft tab tdnone topTabOffer')}
        owners['Właściciel']['param'] = re.search(self.SEARCH_PATTERN,
                                                  urllib.parse.unquote(self.BASE_CONTENT.find(
                                                      'a', class_='fleft tab tdnone topTabOffer')['href'])).group()
        return owners

    def _get_filters_photos(self):
        """ Get photo filter """
        photos = {'Tylko ze zdjęciem': {'param': self.BASE_CONTENT.find(
            'input', id='photo-only')['name'],
            'values': self.BASE_CONTENT.find(
            'input', id='photo-only')['value']}}
        return photos

    def _get_filters_order(self):
        """ Get order (newest first) filter """
        order = {'Sortuj: Najnowsze': {'param': re.search(self.SEARCH_PATTERN,
                                                          urllib.parse.unquote(self.BASE_CONTENT.find(
                                                              'a', {'data-type': 'created_at:desc'})[
                                                              'data-url'])).group(),
                                       'values': urllib.parse.unquote(self.BASE_CONTENT.find(
                                           'a', {'data-type': 'created_at:desc'})['data-url']).split('=')[-1]}}
        return order

    @staticmethod
    def _get_filters_page():
        """ Get page number filter """
        page_number = {'Strona': {'param': 'page'}}
        return page_number

    def _process_filter(self, name, vals):
        """ Get url params for filter """
        filter_dict = {}
        if name == 'Strona':
            pass  # Don't include page number here
        elif name == 'Dzielnica':
            filter_key = self.filters[name]['param']
            filter_value = self.filters[name]['values'][vals]
            filter_dict[filter_key] = filter_value
        else:
            if vals:  # if filter value is set
                if isinstance(vals, str) or isinstance(vals, int):
                    if self.filters[name].get('values'):
                        if isinstance(self.filters[name]['values'], dict):
                            filter_value = self.filters[name]['values'][vals]
                        else:
                            filter_value = self.filters[name]['values']
                        filter_key = self.filters[name]['param'].format(
                            param_order=0)
                    else:
                        filter_value = vals
                        filter_key = self.filters[name]['param']
                    filter_dict[filter_key] = filter_value
                elif isinstance(vals, list) or isinstance(vals, tuple):
                    for vo, vi in enumerate(vals):
                        filter_value = self.filters[name]['values'][vi]
                        filter_key = self.filters[name]['param'].format(
                            param_order=vo)
                        filter_dict[filter_key] = filter_value
                else:
                    raise TypeError
            else:
                pass
        return filter_dict

    def get_url_params(self):
        """ Get URL based on selected filters """
        filters_applied = {k: None for k, v in self.filters.items(
        )}  # create empty dictionary with filter keys
        # Pre-defined (default) filters
        filters_applied['Tylko ze zdjęciem'] = self.filters['Tylko ze zdjęciem']['values']
        filters_applied['Sortuj: Najnowsze'] = self.filters['Sortuj: Najnowsze']['values']
        filters_applied.update(self.filters_selected)

        self.url_params = []  # reset parameters

        if filters_applied.get('Dzielnica'):
            if isinstance(filters_applied['Dzielnica'], str):
                param_dict = {}
                for name, vals in filters_applied.items():
                    param_dict.update(self._process_filter(name, vals))
                self.url_params.append(param_dict)
            elif isinstance(filters_applied['Dzielnica'], tuple) or \
                    isinstance(filters_applied['Dzielnica'], list):
                filters_iter = filters_applied.copy()
                for district in filters_applied['Dzielnica']:
                    filters_iter['Dzielnica'] = district
                    param_dict = {}
                    for name, vals in filters_iter.items():
                        param_dict.update(self._process_filter(name, vals))
                    self.url_params.append(param_dict)
        else:
            param_dict = {}
            for name, vals in filters_applied.items():
                if name != 'Dzielnica':
                    param_dict.update(self._process_filter(name, vals))
            self.url_params.append(param_dict)
        logging.info(
            f"Following parameters will be passed to URL:\n{pformat(self.url_params)}")

    def get_page(self, param_dict, page_number):
        """ Add page number to url """
        filter_key = self.filters['Strona']['param']
        filter_value = page_number
        param_dict[filter_key] = filter_value
        return param_dict
