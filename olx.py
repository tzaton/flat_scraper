import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

base_url = "https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/warszawa/"
base_site = requests.get(base_url)
base_content = BeautifulSoup(base_site.text, 'lxml')


# Get possible filters
filters = {}
search_pattern = re.compile(r'\w+\[.+\]')  # pattern for filters
for param in base_content.find(class_="clr multifilters subSelectActive").find_all(
        class_=re.compile("param param(Select|Float)")):
    filter_code = param['data-name']
    for filter_item in param.find_all('div', {'class': re.compile('filter-item')}):
        filter_name = filter_item.find('span', {'class': 'header block'}).text
        filter_name = filter_name.replace(b'\xc2\xb2'.decode(), '2')  # Replace square meters
        multiparam = filter_item.find('input', {'class': re.compile('defaultval')})
        if multiparam:
            filter_code = re.search(search_pattern, multiparam['class'][2]).group()
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

# Warsaw district codes
districts = {'Dzielnica': {'param': '', 'values': {}}}
districts['Dzielnica']['values'] = {d.text: d['href'].split('=')[-1]
                                    for d in base_content.find_all('a', {'href': re.compile('district_id')})}
districts['Dzielnica']['param'] = re.search(search_pattern,
                                            urllib.parse.unquote(
                                                base_content.find(
                                                    'a', {'href': re.compile('district_id')})['href'])).group()
filters.update(districts)  # add districts to filter dictionary

# Offer owner
owners = {'Właściciel': {'param': '', 'values': {}}}
owners['Właściciel']['values'] = {[text for text in d.stripped_strings][0]: d['href'].split('=')[-1]
                                  for d in base_content.find_all('a', class_='fleft tab tdnone topTabOffer')}
owners['Właściciel']['param'] = re.search(search_pattern,
                                          urllib.parse.unquote(
                                              base_content.find('a', class_='fleft tab tdnone topTabOffer')['href']
                                          )).group()
filters.update(owners)  # add owners to filter dictionary

# Photos
filters['Tylko ze zdjęciem'] = {'param': base_content.find('input', id='photo-only')['name'],
                                'values': base_content.find('input', id='photo-only')['value']}
# Order
filters['Sortuj: Najnowsze'] = {'param': re.search(search_pattern,
                                                   urllib.parse.unquote(
                                                       base_content.find(
                                                           'a', {'data-type': 'created_at:desc'})['data-url'])).group(),
                                'values': urllib.parse.unquote(base_content.find(
                                    'a', {'data-type': 'created_at:desc'})['data-url']).split('=')[-1]}

# Page number
filters['Strona'] = {'param': 'page'}

# Set filters
selected_filters = {k: None for k, v in filters.items()}  # create empty dictionary with filter keys

# Pre-defined (default) filters
selected_filters['Tylko ze zdjęciem'] = filters['Tylko ze zdjęciem']['values']
selected_filters['Sortuj: Najnowsze'] = filters['Sortuj: Najnowsze']['values']

# User-defined filters
user_filters = {'Umeblowane': 'Tak',
                'Liczba pokoi': ('2 pokoje', '3 pokoje'),
                'Dzielnica': ('Wola', 'Ochota', 'Mokotów', 'Ursynów', 'Bielany', 'Targówek')}
selected_filters.update(user_filters)


def get_url(filter_dict):
    """ Get url based on selected filters """
    request_filters = {}
    for name, vals in filter_dict.items():
        if name not in ('Dzielnica', 'Strona'):  # Don't include district and page number here
            if vals:  # if filter value is set
                filter_key = filters[name]['param']
                if isinstance(vals, str) or isinstance(vals, int):
                    if filters[name].get('values'):
                        if isinstance(filters[name]['values'], dict):
                            filter_value = filters[name]['values'][vals]
                        else:
                            filter_value = filters[name]['values']
                    else:
                        filter_value = vals
                    request_filters[filter_key.format(param_order=0)] = filter_value
                elif isinstance(vals, list) or isinstance(vals, tuple):
                    for vo, vi in enumerate(vals):
                        filter_value = filters[name]['values'][vi]
                        request_filters[filter_key.format(param_order=vo)] = filter_value
                else:
                    raise TypeError
    final_url = requests.get(base_url, params=request_filters).url
    return final_url


def get_url_param(param_name, param_value):
    """ Add parameter to url """
    if filters[param_name].get('values'):
        final_url = f"{urllib.parse.quote(filters[param_name]['param'])}={filters[param_name]['values'][param_value]}"
    else:
        final_url = f"{urllib.parse.quote(filters[param_name]['param'])}={param_value}"
    return final_url


# Get data from website
url_filtered = get_url(selected_filters)
if selected_filters.get('Dzielnica'):
    for district in selected_filters['Dzielnica']:
        k = 1  # start on first page
        while True:
            url = f"{url_filtered}&{get_url_param('Dzielnica', district)}&{get_url_param('Strona', k)}"
            site = requests.get(url)
            if site.url == base_url or re.search(fr"{base_url}\?page=\d+", site.url):  # Skip wrong pages
                break
            print(site.url)
            k += 1
else:
    k = 1  # start on first page
    while True:
        url = f"{url_filtered}&{get_url_param('Strona', k)}"
        site = requests.get(url)
        if site.url == base_url or re.search(fr"{base_url}\?page=\d+", site.url):  # Skip wrong pages
            break
        print(site.url)
        k += 1
