from unittest import TestCase
from metamenth.enumerations import MeasurementUnit
from metamenth.transducers.sensor import Sensor
from metamenth.enumerations import SensorMeasure
from metamenth.enumerations import SensorMeasureType
from metamenth.enumerations import SensorLogType
from metamenth.measure_instruments.sensor_data import SensorData
from metamenth.subsystem.appliance import Appliance
from metamenth.enumerations import ApplianceType
from metamenth.enumerations import ApplianceCategory
from metamenth.datatypes.rated_device_measure import RatedDeviceMeasure
from metamenth.misc import MeasureFactory
from metamenth.datatypes.measure import Measure


class TestAppliance(TestCase):

    def setUp(self) -> None:
        pass

    def test_create_a_smart_bulb_in_a_home(self):
        smart_bulb = Appliance("Smart Light", [ApplianceCategory.HOME, ApplianceCategory.SMART],
                               ApplianceType.LIGHT_BULB)
        self.assertEqual(smart_bulb.appliance_type, ApplianceType.LIGHT_BULB)
        self.assertEqual(smart_bulb.get_transducers(), [])
        self.assertEqual(smart_bulb.appliance_category[0], ApplianceCategory.HOME)
        self.assertEqual(smart_bulb.consumption_capacity, None)

    def test_smart_camera_with_presence_sensor(self):
        smart_camera = Appliance("Smart Camera", [ApplianceCategory.OFFICE, ApplianceCategory.SMART],
                                 ApplianceType.CAMERA)
        presence_sensor = Sensor("PRESENCE.SENSOR", SensorMeasure.OCCUPANCY, MeasurementUnit.PRESENCE,
                                 SensorMeasureType.THERMO_COUPLE_TYPE_A, 0, sensor_log_type=SensorLogType.POLLING)
        smart_camera.add_transducer(presence_sensor)
        self.assertEqual(smart_camera.get_transducer_by_name("PRESENCE.SENSOR"), presence_sensor)
        self.assertEqual(smart_camera.appliance_type, ApplianceType.CAMERA)
        self.assertEqual(smart_camera.get_transducer_by_name("PRESENCE.SENSOR").measure, SensorMeasure.OCCUPANCY)

    def test_thermostat_with_operating_condition(self):
        temp_op_condition = MeasureFactory.create_measure("Continuous",
                                                          Measure(MeasurementUnit.DEGREE_CELSIUS, 4.4, 37.8))
        humidity_op_conditions = MeasureFactory.create_measure("Continuous",
                                                               Measure(MeasurementUnit.RELATIVE_HUMIDITY, 20, 80))
        thermostat = Appliance("Thermostat", [ApplianceCategory.OFFICE, ApplianceCategory.SMART],
                               ApplianceType.THERMOSTAT,
                               operating_conditions=[temp_op_condition, humidity_op_conditions])
        self.assertEqual(thermostat.operating_conditions, [temp_op_condition, humidity_op_conditions])
        self.assertEqual(thermostat.operating_conditions[0].measurement_unit, MeasurementUnit.DEGREE_CELSIUS)
        self.assertEqual(thermostat.operating_conditions[1].minimum, 20)
        self.assertEqual(thermostat.operating_conditions[1].maximum, 80)

    def test_thermostat_with_multiple_sensors(self):
        thermostat = Appliance("Thermostat", [ApplianceCategory.OFFICE, ApplianceCategory.SMART],
                               ApplianceType.THERMOSTAT)
        presence_sensor = Sensor("PRESENCE.SENSOR", SensorMeasure.OCCUPANCY, MeasurementUnit.PRESENCE,
                                 SensorMeasureType.THERMO_COUPLE_TYPE_A, 0, sensor_log_type=SensorLogType.POLLING)
        temp_sensor = Sensor("TEMPERATURE.SENSOR", SensorMeasure.TEMPERATURE, MeasurementUnit.DEGREE_CELSIUS,
                             SensorMeasureType.THERMO_COUPLE_TYPE_A, 900, sensor_log_type=SensorLogType.POLLING)
        humidity_sensor = Sensor("HUMIDITY.SENSOR", SensorMeasure.HUMIDITY, MeasurementUnit.RELATIVE_HUMIDITY,
                                 SensorMeasureType.THERMO_COUPLE_TYPE_A, 900, sensor_log_type=SensorLogType.POLLING)

        thermostat.add_transducer(presence_sensor)
        thermostat.add_transducer(temp_sensor)
        thermostat.add_transducer(humidity_sensor)

        self.assertIsNotNone(thermostat.get_transducers())
        self.assertEqual(len(thermostat.get_transducers()), 3)
        self.assertEqual(thermostat.get_transducer_by_name("TEMPERATURE.SENSOR"), temp_sensor)
        self.assertEqual(thermostat.get_transducer_by_uid(humidity_sensor.UID).data_frequency, 900)

    def test_smart_tv_with_operating_condition_and_consumption_capacity(self):
        temp_op_condition = MeasureFactory.create_measure("Continuous",
                                                          Measure(MeasurementUnit.DEGREE_CELSIUS, 0, 40))
        humidity_op_conditions = MeasureFactory.create_measure("Continuous",
                                                               Measure(MeasurementUnit.RELATIVE_HUMIDITY, 10, 80))
        consumption_capacity = MeasureFactory.create_measure("Binary",
                                                             Measure(MeasurementUnit.WATTS, 50))
        tv = Appliance("TV", [ApplianceCategory.HOME, ApplianceCategory.SMART],
                       ApplianceType.TELEVISION, operating_conditions=[temp_op_condition, humidity_op_conditions],
                       consumption_capacity=consumption_capacity)

        self.assertEqual(tv.consumption_capacity, consumption_capacity)
        self.assertEqual(tv.appliance_type, ApplianceType.TELEVISION)
        self.assertEqual(tv.consumption_capacity.value, 50)
        self.assertEqual(tv.operating_conditions[0].maximum, 40)

    def test_refrigerator_with_rated_device_measure(self):
        voltage_rating = MeasureFactory.create_measure("Binary", Measure(MeasurementUnit.VOLT, 120))
        current_rating = MeasureFactory.create_measure("Binary", Measure(MeasurementUnit.AMPERE, 1))
        rated_device_measure = RatedDeviceMeasure(current_rating=current_rating, voltage_rating=voltage_rating,
                                                  power_factor=0.89)
        consumption_capacity = MeasureFactory.create_measure("Binary",
                                                             Measure(MeasurementUnit.WATTS, 400))
        refrigerator = Appliance("Refrigerator", [ApplianceCategory.HOME, ApplianceCategory.SMART],
                                 ApplianceType.REFRIGERATOR, rated_device_measure=rated_device_measure,
                                 consumption_capacity=consumption_capacity)
        self.assertEqual(refrigerator.rated_device_measure, rated_device_measure)
        self.assertEqual(refrigerator.rated_device_measure.voltage_rating, voltage_rating)
        self.assertEqual(refrigerator.rated_device_measure.current_rating, current_rating)
        self.assertEqual(refrigerator.operating_conditions, [])

    def test_thermostat_with_temperature_sensor_data(self):
        thermostat = Appliance("Thermostat", [ApplianceCategory.OFFICE, ApplianceCategory.SMART],
                               ApplianceType.THERMOSTAT)
        temp_sensor = Sensor("TEMPERATURE.SENSOR", SensorMeasure.TEMPERATURE, MeasurementUnit.DEGREE_CELSIUS,
                             SensorMeasureType.THERMO_COUPLE_TYPE_A, 900, sensor_log_type=SensorLogType.POLLING)
        sensor_data = []
        for temp in range(20, 30):
            sensor_data.append(SensorData(temp))
        temp_sensor.add_data(sensor_data)
        thermostat.add_transducer(temp_sensor)
        self.assertNotEqual(thermostat.get_transducer_by_name("TEMPERATURE.SENSOR").get_data(), [])
        self.assertEqual(thermostat.get_transducer_by_uid(temp_sensor.UID).get_data(), sensor_data)

    def test_remove_sensor_from_appliance(self):
        thermostat = Appliance("Thermostat", [ApplianceCategory.OFFICE, ApplianceCategory.SMART],
                               ApplianceType.THERMOSTAT)
        presence_sensor = Sensor("PRESENCE.SENSOR", SensorMeasure.OCCUPANCY, MeasurementUnit.PRESENCE,
                                 SensorMeasureType.THERMO_COUPLE_TYPE_A, 0, sensor_log_type=SensorLogType.POLLING)
        temp_sensor = Sensor("TEMPERATURE.SENSOR", SensorMeasure.TEMPERATURE, MeasurementUnit.DEGREE_CELSIUS,
                             SensorMeasureType.THERMO_COUPLE_TYPE_A, 900, sensor_log_type=SensorLogType.POLLING)

        thermostat.add_transducer(presence_sensor)
        thermostat.add_transducer(temp_sensor)

        self.assertEqual(thermostat.get_transducers(), [presence_sensor, temp_sensor])
        thermostat.remove_transducer(temp_sensor)
        self.assertEqual(thermostat.get_transducers(), [presence_sensor])

    def test_remove_sensor_data_from_appliance_sensor(self):
        thermostat = Appliance("Thermostat", [ApplianceCategory.OFFICE, ApplianceCategory.SMART],
                               ApplianceType.THERMOSTAT)
        temp_sensor = Sensor("TEMPERATURE.SENSOR", SensorMeasure.TEMPERATURE, MeasurementUnit.DEGREE_CELSIUS,
                             SensorMeasureType.THERMO_COUPLE_TYPE_A, 900, sensor_log_type=SensorLogType.POLLING)

        thermostat.add_transducer(temp_sensor)
        sensor_data = []
        for temp in range(20, 30):
            sensor_data.append(SensorData(temp))
        thermostat.get_transducer_by_name("TEMPERATURE.SENSOR").add_data(sensor_data)

        self.assertEqual(thermostat.get_transducer_by_name("TEMPERATURE.SENSOR").get_data(), sensor_data)
        thermostat.get_transducer_by_name("TEMPERATURE.SENSOR").remove_data(sensor_data[0])
        self.assertNotEqual(thermostat.get_transducer_by_name("TEMPERATURE.SENSOR").get_data(), sensor_data)
        self.assertEqual(thermostat.get_transducer_by_name("TEMPERATURE.SENSOR").get_data(), sensor_data[1:])

