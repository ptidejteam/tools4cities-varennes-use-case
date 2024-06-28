from pathlib import Path
import csv
import sys
from metamenth.transducers.sensor import Sensor
from metamenth.structure.interfaces.abstract_floor_space import AbstractFloorSpace
from metamenth.measure_instruments.sensor_data import SensorData
from metamenth.measure_instruments.weather_station import WeatherStation
from metamenth.measure_instruments.weather_data import WeatherData
from metamenth.datatypes.binary_measure import BinaryMeasure
from metamenth.datatypes.measure import Measure
from metamenth.enumerations import MeasurementUnit
from metamenth.enumerations import DataMeasurementType
from metamenth.measure_instruments.meter import Meter
from metamenth.measure_instruments.meter_measure import MeterMeasure


class DynamicData:

    def __init__(self):
        self.data_directory = Path(__file__).resolve().parent.parent / 'building_structure/data/dynamic'

    def add_sensor_data(self, space_entity: AbstractFloorSpace):
        """
        Reads time series sensor data and populate various sensor with
        historical data.
        NB: The name of the data files corresponds with the name of the sensors
        :param space_entity: the room with some sensor(s)
        :return:
        """
        for sensor in space_entity.get_transducers():
            if isinstance(sensor, Sensor):
                sensor_data_file = self.data_directory / '{}.csv'.format(sensor.name)
                try:
                    with open(sensor_data_file, 'r') as file:
                        csv_reader = csv.reader(file)

                        # skip header row
                        next(csv_reader)
                        sensor_data = []
                        for row in csv_reader:
                            sensor_data.append(SensorData(float(row[1]), row[0]))
                        # add sensor data
                        sensor.add_data(sensor_data)
                except FileNotFoundError:
                    print(f"Error: File '{sensor_data_file}' not found.", file=sys.stderr)
                except ValueError as err:
                    print(err, file=sys.stderr)

    def add_weather_data(self, weather_station: WeatherStation):
        """
        Reads dynamic historical weather data for the weather station
        :return:
        """
        weather_data_file = self.data_directory / 'weather_data.csv'
        try:
            with open(weather_data_file, 'r') as file:
                weather_data = csv.reader(file)
                next(weather_data)
                for row in weather_data:
                    dni_measure = BinaryMeasure(Measure(MeasurementUnit.WATTS_PER_METER_SQUARE, float(row[1])),
                                                DataMeasurementType.DIRECT_NOMINAL_IRRADIANCE)
                    dni = WeatherData(dni_measure, row[0])

                    ghi_measure = BinaryMeasure(Measure(MeasurementUnit.WATTS_PER_METER_SQUARE, float(row[2])),
                                                DataMeasurementType.GLOBAL_HORIZONTAL_IRRADIANCE)
                    ghi = WeatherData(ghi_measure, row[0])

                    dhi_measure = BinaryMeasure(Measure(MeasurementUnit.WATTS_PER_METER_SQUARE, float(row[3])),
                                                DataMeasurementType.DIFFUSE_HORIZONTAL_IRRADIANCE)
                    dhi = WeatherData(dhi_measure, row[0])

                    out_temp_measure = BinaryMeasure(Measure(MeasurementUnit.DEGREE_CELSIUS, float(row[4])),
                                                     DataMeasurementType.OUTSIDE_TEMPERATURE)
                    otm = WeatherData(out_temp_measure, row[0])

                    weather_station.add_weather_data([dni, ghi, dhi, otm])
        except ValueError as err:
            print(err, file=sys.stderr)

    def add_electricity_consumption_data(self, meter: Meter):
        """
        Reads dynamic historical weather data for the weather station
        :return:
        """
        consumption_file = self.data_directory / 'electricity_data.csv'
        try:
            with open(consumption_file, 'r') as file:
                electricity_data = csv.reader(file)
                next(electricity_data)
                for row in electricity_data:
                    print(row)
                    consumed_electricity = MeterMeasure(float(row[1]), row[0],
                                                        DataMeasurementType.CONSUMED_ELECTRICITY)
                    meter.add_meter_measure(consumed_electricity)
        except ValueError as err:
            print(err, file=sys.stderr)
