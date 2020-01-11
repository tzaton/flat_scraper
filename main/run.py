from main.scraper import OLXScraper


selected_filters = {'Umeblowane': 'Tak',
                    'Liczba pokoi': ('2 pokoje', '3 pokoje'),
                    'Cena do': '800000',
                    'Dzielnica': ['Ochota', 'Mokotów'],
                    'Pow. od': '40'
                    }

if __name__ == '__main__':
    scraper = OLXScraper(selected_filters)
    scraper.run()
