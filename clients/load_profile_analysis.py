import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from building_structure.varennes_library import VarennesLibrary
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates


class LoadProfileAnalysis:

    def __init__(self):
        self.library = VarennesLibrary()
        self.library.create_building()
        self.library.add_meter_electricity_consumption_data()
        self.meter = self.library.building.get_meters()[0]
        power_consumption_data = self.meter.get_meter_measures()
        self.electricity_df = pd.DataFrame(
            [{'value': m.value, 'timestamp': m.timestamp} for m in power_consumption_data])

    def consumption_analysis(self):

        hourly_consumption = self.electricity_df.resample('15T', on='timestamp').sum()
        daily_consumption = self.electricity_df.resample('30T', on='timestamp').sum()
        weekly_consumption = self.electricity_df.resample('45T', on='timestamp').sum()
        monthly_consumption = self.electricity_df.resample('H', on='timestamp').sum()

        fig, axs = plt.subplots(4, 1, figsize=(12, 12), sharey=False)  # Create subplots and share the y-axis
        fig.suptitle('Electricity Consumption Analysis')

        self._plot_graph(hourly_consumption, '15 Minutes Profile', 'blue', axs[0])
        self._plot_graph(daily_consumption, '30 Minutes Load Profile', 'black', axs[1])
        self._plot_graph(weekly_consumption, '45 Minutes Load Profile', 'red', axs[2])
        self._plot_graph(monthly_consumption, 'Hourly Load Profile', 'brown', axs[3])

        axs[0].set_ylim(0, 150)
        axs[1].set_ylim(0, 250)
        axs[2].set_ylim(0, 350)
        axs[3].set_ylim(0, 400)

        fig.text(0.04, 0.5, 'Energy Consumption (kWh)', va='center', rotation='vertical', fontsize=12)
        fig.text(0.5, 0.02, 'Date', ha='center', fontsize=12)
        plt.tight_layout(rect=[0.05, 0, 1, 0.96])
        plt.subplots_adjust(bottom=0.1)
        plt.show()

    def compute_load_factor(self):
        """
        Computes the load factor
        :return: load factor, mean electricity consumption, maximum electricity consumption
        """
        return self.electricity_df['value'].mean() / self.electricity_df['value'].max(), \
            self.electricity_df['value'].mean(), self.electricity_df['value'].max()

    def get_periodic_consumption(self, date_from, date_to=None):
        """
        Get consumption statistics (sum, mean, max, min) over a period
        :param date_from: the start date
        :param date_to: the end date
        :return:
        """
        consumption = self.meter.get_meter_measure_by_date(date_from, date_to)
        if consumption:
            consumption_df = pd.DataFrame(
                [{'value': m.value, 'timestamp': m.timestamp} for m in consumption])
            return consumption_df['value'].sum(), consumption_df['value'].mean(), \
                consumption_df['value'].min(), consumption_df['value'].max()
        return 0.0

    def _extract_consumption(self, dataframe, consumption_type='peak'):
        """
        Extract consumption patterns, e.g., minimum consumption
        :param dataframe: the pandas dataframe
        :param consumption_type: the consumption type, minimum or peak consumption
        :return: [index, value]
        """
        value_index = dataframe['value'].idxmin() if consumption_type == 'minimum' else dataframe['value'].idxmax()
        value = dataframe.loc[value_index, 'value']
        return value_index, value

    def _format_func(self, value, tick_number):
        if value >= 1000000:
            return '{:.0f}M'.format(value * 1e-6)
        elif value >= 1000:
            return '{:.0f}K'.format(value * 1e-3)
        else:
            return '{:.0f}'.format(value)

    def _plot_graph(self, dataframe, title, color, axs):
        """
        Plots a graph
        :param dataframe: the pandas dataframe
        :param title: the title of the graph
        :param color: the color of the graph
        :param axs: the plot axis
        :return: None
        """
        axs.plot(dataframe.index, dataframe['value'], marker='o', linestyle='-',
                 color=color, markersize=2)
        axs.xaxis.set_major_locator(mdates.DayLocator(interval=10))
        peak_hourly_idx, peak_hourly = self._extract_consumption(dataframe)
        axs.scatter(peak_hourly_idx, peak_hourly, color='red', label='Peak Demand')

        minimum_hourly_idx, minimum_hourly = self._extract_consumption(dataframe, 'minimum')
        axs.scatter(minimum_hourly_idx, minimum_hourly, color='green', label='Minimum Demand')
        axs.set_title(title)
        axs.yaxis.set_major_formatter(FuncFormatter(self._format_func))
        axs.grid(alpha=0.3)


if __name__ == "__main__":
    obj = LoadProfileAnalysis()
    load_factor, mean_electricity, max_electricity = obj.compute_load_factor()
    print("Max Consumption:", max_electricity)
    print("Average Consumption:", mean_electricity)
    print("Load Factor:", load_factor)
    obj.consumption_analysis()
