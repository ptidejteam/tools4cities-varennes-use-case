from unittest import TestCase
from metamenth.misc import MeasureFactory
from metamenth.enumerations import RecordingType
from metamenth.datatypes.measure import Measure
from metamenth.enumerations import MeasurementUnit
from metamenth.transducers.sensor import Sensor
from metamenth.enumerations import SensorMeasure
from metamenth.enumerations import SensorMeasureType
from metamenth.enumerations import SensorLogType
from metamenth.measure_instruments.sensor_data import SensorData
from time import sleep


class TestSensor(TestCase):

    def setUp(self) -> None:
        self.density_measure = MeasureFactory.create_measure(RecordingType.BINARY.value,
                                                             Measure(MeasurementUnit.KILOGRAM_PER_CUBIC_METER, 0.5))
        self.hc_measure = MeasureFactory.create_measure(RecordingType.BINARY.value,
                                                        Measure(MeasurementUnit.JOULES_PER_KELVIN, 4.5))
        self.tt_measure = MeasureFactory.create_measure(RecordingType.BINARY.value,
                                                        Measure(MeasurementUnit.WATTS_PER_SQUARE_METER_KELVIN, 2.5))
        self.material = None

    def test_temperature_sensor_with_no_measure_frequency(self):
        try:
            Sensor("TEMP.SENSOR", SensorMeasure.TEMPERATURE, MeasurementUnit.DEGREE_CELSIUS,
                   SensorMeasureType.THERMO_COUPLE_TYPE_A, None)
        except ValueError as err:
            self.assertEqual(err.__str__(), "data_frequency must be float")

    def test_co2_sensor_with_temperature_measurement(self):
        try:
            Sensor("CO2.SENSOR", SensorMeasure.CARBON_DIOXIDE, MeasurementUnit.DEGREE_CELSIUS,
                   SensorMeasureType.THERMO_COUPLE_TYPE_A, 5)
        except ValueError as err:
            self.assertEqual(err.__str__(), "CarbonDioxide sensor can not have °C measurement unit")

    def test_pressure_sensor_with_gas_velocity_measurement(self):
        try:
            Sensor("PRESSURE.SENSOR", SensorMeasure.PRESSURE, MeasurementUnit.METERS_PER_SECOND,
                   SensorMeasureType.THERMO_COUPLE_TYPE_A, 5)
        except ValueError as err:
            self.assertEqual(err.__str__(), "Pressure sensor can not have m/s measurement unit")

    def test_air_volume_sensor_with_luminance_measurement(self):
        try:
            Sensor("AIR.VOLUME.SENSOR", SensorMeasure.AIR_VOLUME, MeasurementUnit.CANDELA_PER_SQUARE_METER,
                   SensorMeasureType.THERMO_COUPLE_TYPE_A, 5)
        except ValueError as err:
            self.assertEqual(err.__str__(),
                             "AirVolume sensor can not have cd/m2 measurement unit")

    def test_smoke_sensor_with_noise_measurement(self):
        try:
            Sensor("SMOKE.SENSOR", SensorMeasure.SMOKE, MeasurementUnit.DECIBELS,
                   SensorMeasureType.THERMO_COUPLE_TYPE_A, 5)
        except ValueError as err:
            self.assertEqual(err.__str__(), "Smoke sensor can not have dB measurement unit")

    def test_current_sensor_with_60_seconds_data_interval(self):
        current_sensor = Sensor("CURRENT.SENSOR", SensorMeasure.CURRENT, MeasurementUnit.AMPERE,
                                SensorMeasureType.THERMO_COUPLE_TYPE_A, 60)
        self.assertEqual(current_sensor.data_frequency, 60)
        self.assertEqual(current_sensor.measure.value, SensorMeasure.CURRENT.value)
        self.assertEqual(current_sensor.sensor_log_type, SensorLogType.POLLING)
        self.assertEqual(current_sensor.meta_data, {})

    def test_cov_smoke_sensor_with_metadata(self):
        smoke_sensor = Sensor("SMOKE.SENSOR", SensorMeasure.SMOKE, MeasurementUnit.MICROGRAM_PER_CUBIC_METER,
                              SensorMeasureType.THERMO_COUPLE_TYPE_B, 10)
        self.assertEqual(smoke_sensor.data_frequency, 10)
        smoke_sensor.sensor_log_type = SensorLogType.CHANGE_OF_VALUE
        self.assertEqual(smoke_sensor.sensor_log_type, SensorLogType.CHANGE_OF_VALUE)

        metadata = {'default_data_interval': 10, 'description': 'change of value based on peak threshold'}
        smoke_sensor.meta_data = metadata
        self.assertEqual(smoke_sensor.meta_data, metadata)
        self.assertEqual(smoke_sensor.meta_data['default_data_interval'], 10)

    def test_remove_metadata_from_sensor(self):
        smoke_sensor = Sensor("SMOKE.SENSOR", SensorMeasure.SMOKE, MeasurementUnit.MICROGRAM_PER_CUBIC_METER,
                              SensorMeasureType.THERMO_COUPLE_TYPE_B, 10)

        metadata = {'default_data_interval': 10, 'description': 'change of value based on peak threshold'}
        smoke_sensor.meta_data = metadata
        self.assertEqual(smoke_sensor.meta_data, metadata)
        smoke_sensor.remove_meta_data('default_data_interval')
        self.assertEqual(smoke_sensor.meta_data, {'description': 'change of value based on peak threshold'})

    def test_co2_sensor_with_current_value(self):
        co2_sensor = Sensor("CO2.SENSOR", SensorMeasure.CARBON_DIOXIDE, MeasurementUnit.PARTS_PER_MILLION,
                            SensorMeasureType.THERMO_COUPLE_TYPE_B, 70)
        co2_sensor.current_value = 0.389
        self.assertEqual(co2_sensor.current_value, 0.389)
        self.assertEqual(co2_sensor.measure, SensorMeasure.CARBON_DIOXIDE)

    def test_direct_radiation_sensor_with_input_voltage_rage(self):
        rad_sensor = Sensor("DIR.RADIATION.SENSOR", SensorMeasure.DIRECT_RADIATION,
                            MeasurementUnit.WATTS_PER_METER_SQUARE,
                            SensorMeasureType.THERMO_COUPLE_TYPE_B, 70)
        input_voltage_range = MeasureFactory.create_measure(RecordingType.CONTINUOUS.value,
                                                            Measure(MeasurementUnit.VOLT, 0.5, 0.8))
        rad_sensor.input_voltage_range = input_voltage_range
        self.assertEqual(rad_sensor.input_voltage_range, input_voltage_range)
        self.assertEqual(rad_sensor.input_voltage_range.measurement_unit, MeasurementUnit.VOLT)
        self.assertEqual(rad_sensor.input_voltage_range.minimum, 0.5)
        self.assertEqual(rad_sensor.input_voltage_range.maximum, 0.8)
        self.assertEqual(rad_sensor.input_voltage_range.measure_type, None)

    def test_daylight_sensor_with_output_current_rage(self):
        daylight_sensor = Sensor("DAYLIGHT.SENSOR", SensorMeasure.DAYLIGHT,
                                 MeasurementUnit.LUX,
                                 SensorMeasureType.THERMO_COUPLE_TYPE_C, 70)
        output_current_range = MeasureFactory.create_measure(RecordingType.CONTINUOUS.value,
                                                             Measure(MeasurementUnit.AMPERE, 0.023, 0.017))
        daylight_sensor.output_current_range = output_current_range
        self.assertEqual(daylight_sensor.output_current_range, output_current_range)
        self.assertEqual(daylight_sensor.output_current_range.measurement_unit, MeasurementUnit.AMPERE)
        self.assertEqual(daylight_sensor.output_current_range.minimum, 0.023)
        self.assertEqual(daylight_sensor.output_current_range.maximum, 0.017)
        self.assertEqual(daylight_sensor.input_current_range, None)
        self.assertEqual(daylight_sensor.input_voltage_range, None)
        self.assertEqual(daylight_sensor.output_voltage_range, None)

    def test_add_data_to_sensor(self):
        co2_sensor = Sensor("CO2.SENSOR", SensorMeasure.CARBON_DIOXIDE,
                            MeasurementUnit.PARTS_PER_MILLION,
                            SensorMeasureType.THERMO_COUPLE_TYPE_C, 70)
        data_point_one = SensorData(180)
        data_point_two = SensorData(187)
        data_point_three = SensorData(204)
        co2_sensor.add_data([data_point_one, data_point_two, data_point_three])
        self.assertEqual(len(co2_sensor.get_data()), 3)
        self.assertEqual(co2_sensor.get_data()[0], data_point_one)
        self.assertEqual(co2_sensor.get_data()[1].value, data_point_two.value)

    def test_remove_data_to_sensor(self):
        co2_sensor = Sensor("CO2.SENSOR", SensorMeasure.CARBON_DIOXIDE,
                            MeasurementUnit.PARTS_PER_MILLION,
                            SensorMeasureType.THERMO_COUPLE_TYPE_C, 70)
        data_point_one = SensorData(180)
        data_point_two = SensorData(187)
        data_point_three = SensorData(204)
        co2_sensor.add_data([data_point_one, data_point_two, data_point_three])

        co2_sensor.remove_data(data_point_two)
        self.assertEqual(len(co2_sensor.get_data()), 2)
        self.assertEqual(co2_sensor.get_data(), [data_point_one, data_point_three])

    def test_search_sensor_data_with_date(self):
        co2_sensor = Sensor("CO2.SENSOR", SensorMeasure.CARBON_DIOXIDE,
                            MeasurementUnit.PARTS_PER_MILLION,
                            SensorMeasureType.THERMO_COUPLE_TYPE_C, 70)

        sensor_data = []
        for data in range(180, 200):
            sensor_data.append(SensorData(data))
            sleep(0.5)
        co2_sensor.add_data(sensor_data)
        returned_data = co2_sensor.get_data_by_date(str(sensor_data[10].timestamp))
        self.assertGreater(returned_data[0].timestamp, sensor_data[0].timestamp)
        self.assertEqual(len(returned_data), 10)

    def test_search_sensor_data_with_date_range(self):
        co2_sensor = Sensor("CO2.SENSOR", SensorMeasure.CARBON_DIOXIDE,
                            MeasurementUnit.PARTS_PER_MILLION,
                            SensorMeasureType.THERMO_COUPLE_TYPE_C, 70)

        sensor_data = []
        for data in range(190, 200):
            sensor_data.append(SensorData(data))
            sleep(0.5)
        co2_sensor.add_data(sensor_data)
        returned_data = co2_sensor.get_data_by_date(str(sensor_data[0].timestamp), str(sensor_data[2].timestamp))
        self.assertEqual(returned_data[0].timestamp, sensor_data[0].timestamp)
        self.assertEqual(returned_data[2].timestamp, sensor_data[2].timestamp)

