# Real estate market data scraper
Get data on real estate sale offers in Warsaw using customizable filters.

## Supported platforms
### Current status
- [x] olx.pl
- [x] otodom.pl (only offers hosted on olx.pl)
- [ ] gumtree.pl

## How to use
1. In `run.py` define filters you want to apply in search
2. Run `run.py`
3. The results (list of offers which meet the criteria) will be available as json file. By default it's `data/scraper_data.json`

## Prerequisites
Polish locale has to be installed.
### Linux
```bash
sudo apt-get install language-pack-pl
```
