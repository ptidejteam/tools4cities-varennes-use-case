from unittest import TestCase
from metamenth.measure_instruments.weather_station import WeatherStation
from metamenth.measure_instruments.weather_data import WeatherData
from metamenth.enumerations import DataMeasurementType
from metamenth.misc import MeasureFactory
from metamenth.enumerations import RecordingType
from metamenth.datatypes.measure import Measure
from metamenth.enumerations import MeasurementUnit
import copy


class TestWeatherStation(TestCase):

    def setUp(self) -> None:
        self.station = WeatherStation('Station One')
        self.temp_measure = MeasureFactory.create_measure(RecordingType.BINARY.value,
                                                          Measure(MeasurementUnit.DEGREE_CELSIUS, -8))
        self.temp_measure.measure_type = DataMeasurementType.OUTSIDE_TEMPERATURE

    def test_weather_station_with_no_location_and_data(self):
        self.assertEqual(self.station.location, "")
        self.assertIsInstance(self.station.UID, str)
        self.assertEqual(len(self.station.get_weather_data()), 0)

    def test_weather_station_with_invalid_location(self):
        try:
            self.station.location = "Montreal"
        except ValueError as err:
            self.assertEqual(err.__str__(), "Location should be a string of three words delimited with two periods.")

    def test_weather_station_data(self):
        weather_data = WeatherData(self.temp_measure)
        self.assertEqual(weather_data.data.measurement_unit, MeasurementUnit.DEGREE_CELSIUS)
        self.assertEqual(weather_data.data.measurement_unit.value, "°C")
        self.assertEqual(weather_data.data.value, -8)
        self.assertEqual(weather_data.data.measure_type, DataMeasurementType.OUTSIDE_TEMPERATURE)

    def test_weather_station_with_data(self):
        temp_data = WeatherData(self.temp_measure)
        wind_measure = copy.deepcopy(self.temp_measure)
        wind_measure.measurement_unit = MeasurementUnit.METERS_PER_SECOND
        wind_measure.value = 3.5
        wind_measure.measure_type = DataMeasurementType.WIND_SPEED
        wind_speed_data = WeatherData(wind_measure)
        self.station.add_weather_data([temp_data, wind_speed_data])
        self.assertEqual(len(self.station.get_weather_data()), 2)
        self.assertEqual(self.station.get_weather_data()[0], temp_data)
        self.assertIsInstance(self.station.get_weather_data()[0], WeatherData)
        self.assertEqual(self.station.get_weather_data()[1].data.value, 3.5)
        self.assertEqual(self.station.get_weather_data()[1].data.measurement_unit, MeasurementUnit.METERS_PER_SECOND)
        self.assertEqual(self.station.get_weather_data()[1].data.measure_type, DataMeasurementType.WIND_SPEED)


