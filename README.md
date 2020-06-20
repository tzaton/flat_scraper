# Real estate market data scraper
Get and analyze data on real estate sale offers in Warsaw, Poland.

## Project description
 Using this package you can get the latest flat sales offers from Warsaw selected according to your preferences. The data is collected from popular advertising portals (see [Supported platforms](#Supported-platforms)) and saved for browsing or further analysis.

## Supported platforms
- [x] olx.pl
- [x] otodom.pl (only offers hosted on olx.pl)

## Project structure
```
.
|-- README.md
|-- __init__.py
|-- img
|   |-- price_hist.png
|   `-- price_median.png
|-- logging.json
|-- main
|   |-- __init__.py
|   |-- analysis
|   |   |-- __init__.py
|   |   `-- analyzer.py
|   `-- webscraping
|       |-- __init__.py
|       |-- ad.py
|       |-- filter.py
|       |-- offer.py
|       `-- scraper.py
|-- requirements.txt
|-- run.py
`-- utils
    |-- __init__.py
    |-- logging_config.py
    `-- set_locale.py
```

### main/webscraping
Subpackage responsible for scraping data from the advertising portal.
- `filter.py` - get available filters, translate filters into URL, set filters according to user definition
- `ad.py` - collect information from websites with advertisements (price, date added etc.)
- `offer.py` - collect information from offers (number of rooms, floor etc.)
- `scraper.py` - create a scraper to browse the portal and find offers

### main/analysis
Subpackage responsible for the analysis of collected flat offer data.
- `analyzer.py` - read offer data, summarize price in total and across districts

### utils
Contains small utility functions
- `logging_config.py` - configure logging from json file. Use another logging configuration if you prefer.
- `set_locale.py` - change locale within context (used for handling local time definitions)


## How to use
In `run.py` file you can find an example usage of this package.
1. Define filters you want to apply for search
    ```python
    # Define parameters for search
    # See available filters and values
    # on https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/warszawa/

    selected_filters = {'Umeblowane': 'Tak',
                        'Liczba pokoi': ('2 pokoje', '3 pokoje'),
                        'Cena do': '700000',
                        'Dzielnica': ['Bemowo', 'Włochy', 'Wola', 'Ursynów',
                                    'Śródmieście', 'Ochota', 'Mokotów'],
                        'Pow. od': '40'
                        }
    ```
2. Run scraper and export collected data to file.
   ```python
   # Run scraper
   scraper = OLXScraper(selected_filters)
   scraper.run()

   # Export data
   data_file = Path('.') / "data" / "scraper_data.json"
   scraper.export_data(data_file)
   ```
3. Read collected data and run price analysis. The results are pandas DataFrames and plots.
```python
    # Read and analyze data
    ofan = OfferAnalyzer(data_file)
    price_summary = ofan.get_price_summary()
    price_district_summary = ofan.get_price_district_summary()
    ofan.show_plots()
```

### Note
- By default log files are stored in *log/*. See `run.py`
- By default data files are stored in *data/*. See `run.py`

## Example output
- Price histogram
    ![Price histogram](img/price_hist.png?raw=true "Price histogram")
- Price median per district
    ![Price median](img/price_median.png?raw=true "Price median")


## Prerequisites
See dependencies for a conda environment in `requirements.txt`.

Polish locale has to be installed.
#### Ubuntu
```bash
sudo apt-get install language-pack-pl
```
