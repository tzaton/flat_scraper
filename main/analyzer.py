"""Summarize and analyze collected offer data
"""

import logging
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

# Logger
logger = logging.getLogger(__name__)


class OfferAnalyzer:
    def __init__(self, offer_datafile):
        # Read flat data
        self.offer_data = pd.read_json(offer_datafile)
        logger.debug(f"Offer data:\n{self.offer_data.head()}")
        logger.debug(
            f"Available columns are: {', '.join(self.offer_data.columns)}")

    def get_price_summary(self):
        """Summarize price (total and per meter)
        """
        fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(10, 7))
        plt.subplot(2, 1, 1)
        self._plot_price_histogram(self.offer_data['price'],
                                   title="Price distribution",
                                   x_tick_interval=50000,
                                   color="darkcyan")
        plt.subplot(2, 1, 2)
        self._plot_price_histogram(self.offer_data['price_meter'],
                                   title="Price/m\u00B2 distribution",
                                   x_tick_interval=1000,
                                   color="darkcyan")
        plt.tight_layout()
        plt.show(block=False)
        plt.show()

    @staticmethod
    def _plot_price_histogram(price_data, title, x_tick_interval, **kwargs):
        price_data = price_data.dropna()
        with plt.style.context('bmh'):
            n_bins = 20
            ax = price_data.hist(bins=n_bins, alpha=0.7, **kwargs)

            plt.title(title)
            plt.xlabel("price")
            plt.ylabel("number of offers")

            plt.xticks(rotation=45)
            ax.xaxis.set_major_locator(
                ticker.MultipleLocator(base=x_tick_interval))
            ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

            # Add median price
            median_price = price_data.median()
            hist_y, hist_x = np.histogram(price_data, bins=n_bins)
            plt.axvline(median_price, color='midnightblue', linewidth=2)
            plt.text(median_price, np.quantile(hist_y, 0.3), s=f"Median price={median_price:,.0f} z\u0142", rotation=90,
                     horizontalalignment="right",
                     verticalalignment="bottom")