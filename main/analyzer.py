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
        self.offer_datafile = offer_datafile
        # Read flat data
        self.offer_data = pd.read_json(offer_datafile)
        logger.info(f"Loaded data from file: {self.offer_datafile}")
        logger.debug(f"Offer data:\n{self.offer_data.head()}")
        logger.debug(
            f"Available columns are: {', '.join(self.offer_data.columns)}")

    def get_price_summary(self):
        """Summarize price (total and per meter)
            Calculate descriptive statistics and plot histograms

        Returns
        -------
        pd.DataFrame
            Price descriptive statistics
        """
        price_summary = self.offer_data.loc[:, [
            'price', 'price_meter']].describe()
        price_summary.columns = ['Price', 'Price/m\u00B2']
        with pd.option_context('precision', 0):
            logger.info(f"\n{price_summary}")

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
                                   color="sienna")
        plt.tight_layout()
        plt.show(block=False)
        plt.show()

        return price_summary

    @staticmethod
    def _plot_price_histogram(price_data, title, x_tick_interval, **kwargs):
        """ Plot histogram of price

        Parameters
        ----------
        price_data : pd.Series
            price data
        title : str
            plot title
        x_tick_interval : int
            interval for x axis
        """
        price_data = price_data.dropna()
        n_obs = len(price_data)

        with plt.style.context('bmh'):
            n_bins = 20
            ax = price_data.hist(bins=n_bins, alpha=0.9, **kwargs)

            ax.grid(linewidth=0.5)

            plt.title(title)
            plt.xlabel("price")
            plt.ylabel("number of offers")

            # Format X axis
            plt.xticks(rotation=45)
            ax.xaxis.set_major_locator(
                ticker.MultipleLocator(base=x_tick_interval))
            ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

            # Add median price
            median_price = price_data.median()
            hist_y, hist_x = np.histogram(price_data, bins=n_bins)
            plt.axvline(median_price, color='midnightblue', linewidth=2)
            plt.text(median_price, np.quantile(hist_y, 0.25), s=f"Median price={median_price:,.0f} z\u0142", rotation=90,
                     horizontalalignment="right",
                     verticalalignment="bottom")

            # Add number of observations
            plt.text(hist_x.min(), hist_y.max() * 0.9, s=f"Total number of offers={n_obs}",
                     horizontalalignment="left")

    def get_price_district_summary(self):
        """Summarize price by district

        Returns
        -------
        pd.DataFrame
            Price descriptive statistics grouped by district
        """
        # Group by district, sort by median price per meter
        price_district_summary = self.offer_data.loc[:, [
            'district', 'price', 'price_meter']].groupby('district').describe()\
            .sort_values(by=('price_meter', '50%'), ascending=False)
        price_district_summary.columns.set_levels(
            ['Price', 'Price/m\u00B2'], level=0, inplace=True)

        # View summary
        with pd.option_context('precision', 0):
            logger.info(f"\n{price_district_summary}")

        # Plots
        fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(10, 7))
        plt.subplot(2, 1, 1)
        self._plot_price_by_district(
            price_district_summary, 'Price', 50000, color="darkcyan")
        plt.subplot(2, 1, 2)
        self._plot_price_by_district(
            price_district_summary, 'Price/m\u00B2', 1000, color="sienna")
        plt.tight_layout()
        plt.show(block=False)
        plt.show()

        return price_district_summary

    @staticmethod
    def _plot_price_by_district(price_data, column_name, x_tick_interval, **kwargs):
        chart_data = price_data.loc[:, (column_name, '50%')].sort_values()
        with plt.style.context('bmh'):
            ax = chart_data.plot.barh(**kwargs)
            ax.grid(axis='y')

            plt.title(f"{column_name} median")

            # Format X axis
            plt.xticks(rotation=45)
            ax.xaxis.set_major_locator(
                ticker.MultipleLocator(base=x_tick_interval))
            ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
