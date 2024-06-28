import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from building_structure.varennes_library import VarennesLibrary


class IndoorAirQuality:

    def __init__(self, spaces: []):
        self._spaces = spaces
        self.co2_concentration = {}
        for space in self._spaces:
            for space_sensor in space.get_transducers():
                if space_sensor.measure.value == 'CarbonDioxide':
                    self.co2_concentration[space.name + ' ' + space_sensor.name] = pd.DataFrame(
                        [{'value': m.value, 'timestamp': m.timestamp} for m in space_sensor.get_data()])

    def analyse_air_quality(self):
        plt.figure(figsize=(12, 6))
        for room_sensor_name, c02_concentration_df in self.co2_concentration.items():
            c02_concentration_df.set_index('timestamp', inplace=True)

            plt.plot(c02_concentration_df.index, c02_concentration_df,
                     label=room_sensor_name, zorder=5)
            plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
            plt.xticks(rotation=45)
            peak_idx = c02_concentration_df['value'].idxmax()
            peak_value = c02_concentration_df.loc[peak_idx, 'value']
            plt.scatter(peak_idx, peak_value)

            min_idx = c02_concentration_df['value'].idxmin()
            min_value = c02_concentration_df.loc[min_idx, 'value']
            plt.scatter(min_idx, min_value)

        plt.axhline(y=1000, color='r', linestyle='--', zorder=1)
        plt.axhline(y=400, color='g', linestyle='--', zorder=1)
        df = list(self.co2_concentration.values())[0]
        # Fill between the lines
        # Clipping the values to stay within the range for shading
        clipped_values = df['value'].clip(lower=400, upper=1000)

        # Fill between the lines with clipped values
        plt.fill_between(df.index, 400, 1000,
                         where=(400 <= clipped_values) & (clipped_values <= 1000),
                         color='gray', alpha=0.1, zorder=2)

        plt.xlabel('Time')
        plt.ylabel('CO2 Concentration (ppm)')
        plt.title('Indoor Air Quality Monitoring')
        plt.legend()
        plt.grid(alpha=0.3)
        plt.show()


if __name__ == "__main__":
    library = VarennesLibrary()
    library.create_building()
    library.add_sensor_data()
    # Analyse air quality in rooms on a floor

    iaq = IndoorAirQuality(
        library.building.get_floor_by_number(1).get_rooms({'room_type': 'Office'})
    )

    iaq.analyse_air_quality()

    # Analyse air quality in rooms in a zone
    iaq_2 = IndoorAirQuality(
        library.building.get_zone_by_name('Zone 1').get_spaces()
    )
    iaq_2.analyse_air_quality()




