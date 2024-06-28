from metamenth.enumerations import OpenSpaceType
from metamenth.structure.floor import Floor
from metamenth.enumerations import FloorType
from metamenth.structure.building import Building
from metamenth.datatypes.operational_schedule import OperationalSchedule
from datetime import datetime
from datetime import timedelta
from metamenth.enumerations import BuildingType
import copy
from metamenth.datatypes.zone import Zone
from metamenth.enumerations import ZoneType
from metamenth.enumerations import HVACType
from metamenth.measure_instruments.meter import Meter
from metamenth.enumerations import MeasurementUnit
from metamenth.enumerations import MeterType
from metamenth.measure_instruments.weather_station import WeatherStation
from metamenth.tests.structure.base_test import BaseTest
from metamenth.enumerations import MaterialType
from metamenth.structure.cover import Cover
from metamenth.structure.envelope import Envelope
from metamenth.enumerations import CoverType
from metamenth.enumerations import RoomType
from metamenth.observers.structure_state_change_logger import StructureStateChangeLogger
from metamenth.enumerations import MeterMeasureMode


class TestBuilding(BaseTest):

    def test_building_with_no_address(self):
        try:
            Building(2009, self.height, self.floor_area, self.internal_mass, None, BuildingType.COMMERCIAL, [])
        except ValueError as err:
            self.assertEqual(err.__str__(), "address must be of type Address")

    def test_building_with_no_floor(self):
        try:
            Building(2009, self.height, self.floor_area, self.internal_mass, self.address, BuildingType.COMMERCIAL, [])
        except ValueError as err:
            self.assertEqual(err.__str__(), "floors must be of type [Floor] and must not be empty")

    def test_building_with_no_floor_area(self):
        try:
            Building(2009, self.height, None, self.internal_mass, self.address, BuildingType.COMMERCIAL, [])
        except ValueError as err:
            self.assertEqual(err.__str__(), "floor_area must be of type AbstractMeasure")

    def test_building_with_floor_with_no_room_or_open_space(self):
        try:
            floor = Floor(self.floor_area, 1, FloorType.REGULAR)
            Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                     BuildingType.COMMERCIAL, [floor])
        except ValueError as err:
            self.assertEqual(err.__str__(), "A floor must have at least one room or one open space.")

    def test_building_with_one_floor(self):
        floor = Floor(self.floor_area, 1, FloorType.REGULAR, rooms=[self.room])
        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.COMMERCIAL, [floor])
        self.assertEqual(building.get_floors(), [floor])
        self.assertEqual(building.get_floors()[0].get_rooms(), [self.room])
        self.assertEqual(building.internal_mass, self.internal_mass)
        self.assertEqual(building.building_type, BuildingType.COMMERCIAL)

    def test_residential_building_with_two_floors(self):
        first_floor = Floor(self.floor_area, 1, FloorType.REGULAR, rooms=[self.room])
        second_floor = copy.deepcopy(first_floor)
        second_floor.number = 2
        second_floor.floor_type = FloorType.ROOFTOP
        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.RESIDENTIAL, [first_floor, second_floor])
        self.assertEqual(len(building.get_floors()), 2)
        self.assertEqual(building.get_floor_by_number(1).number, 1)
        self.assertEqual(building.get_floor_by_number(2).number, 2)
        self.assertEqual(building.building_type, BuildingType.RESIDENTIAL)
        self.assertEqual(building.get_floor_by_number(2).floor_type, FloorType.ROOFTOP)

    def test_residential_building_with_appliances(self):
        self.room.add_appliance(self.thermostat)
        self.room.add_appliance(self.smart_camera)
        first_floor = Floor(self.floor_area, 1, FloorType.REGULAR, rooms=[self.room])
        second_floor = copy.deepcopy(first_floor)
        second_floor.number = 2
        second_floor.floor_type = FloorType.ROOFTOP
        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.RESIDENTIAL, [first_floor, second_floor])

        self.assertEqual(len(building.get_floors()), 2)
        self.assertEqual(building.building_type, BuildingType.RESIDENTIAL)
        self.assertEqual(building.get_floor_by_number(1).get_room_by_name(self.room.name).get_appliances(),
                         [self.thermostat, self.smart_camera])
        self.assertEqual(building.get_floor_by_number(1).get_room_by_name(self.room.name)
                         .get_appliance_by_uid(self.thermostat.UID), self.thermostat)

    def test_add_floor_to_existing_building(self):
        first_floor = Floor(self.floor_area, 1, FloorType.REGULAR, rooms=[self.room])

        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.RESIDENTIAL, [first_floor])
        second_floor = copy.deepcopy(first_floor)
        second_floor.number = 2
        second_floor.floor_type = FloorType.ROOFTOP
        building.add_floors([second_floor])

        self.assertEqual(len(building.get_floors()), 2)
        self.assertEqual(building.get_floor_by_number(2), second_floor)

    def test_get_floor_by_uid(self):
        first_floor = Floor(self.floor_area, 1, FloorType.REGULAR, rooms=[self.room])

        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.RESIDENTIAL, [first_floor])

        floor = building.get_floor_by_uid(first_floor.UID)
        self.assertEqual(floor, first_floor)
        self.assertEqual(floor.floor_type, FloorType.REGULAR)

    def test_get_floor_by_number(self):
        first_floor = Floor(self.floor_area, 1, FloorType.REGULAR, rooms=[self.room])

        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.RESIDENTIAL, [first_floor])

        floor = building.get_floor_by_number(1)
        self.assertEqual(floor, first_floor)
        self.assertEqual(floor.floor_type, FloorType.REGULAR)

    def test_get_floor_with_wrong_number(self):
        first_floor = Floor(self.floor_area, 1, FloorType.REGULAR, rooms=[self.room])

        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.RESIDENTIAL, [first_floor])

        floor = building.get_floor_by_number(2)
        self.assertIsNone(floor)

    def test_remove_floor_from_building(self):
        first_floor = Floor(self.floor_area, 1, FloorType.REGULAR, rooms=[self.room])
        second_floor = copy.deepcopy(first_floor)
        second_floor.number = 2
        second_floor.floor_type = FloorType.ROOFTOP
        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.RESIDENTIAL, [first_floor, second_floor])

        building.remove_floor(first_floor)
        self.assertEqual(building.get_floors(), [second_floor])
        self.assertEqual(len(building.get_floors()), 1)
        self.assertEqual(building.get_floor_by_number(second_floor.number).floor_type, FloorType.ROOFTOP)

    def test_add_open_space_to_building_floor(self):
        first_floor = Floor(self.floor_area, 1, FloorType.REGULAR, rooms=[self.room])
        second_floor = copy.deepcopy(first_floor)
        second_floor.number = 2
        second_floor.floor_type = FloorType.ROOFTOP
        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.RESIDENTIAL, [first_floor, second_floor])
        building.get_floor_by_number(1).add_open_spaces([self.hall])
        self.assertEqual(building.get_floor_by_number(1).get_open_spaces(), [self.hall])
        self.assertEqual(building.get_floor_by_number(1).get_open_space_by_name(self.hall.name).space_type,
                         OpenSpaceType.HALL)

    def test_create_building_using_builder(self):
        first_floor = Floor(self.floor_area, 1, FloorType.REGULAR, rooms=[self.room])
        second_floor = Floor(self.floor_area, 2, FloorType.REGULAR, open_spaces=[self.hall])
        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.RESIDENTIAL, [first_floor]).add_floors([second_floor]) \
            .add_open_space(first_floor.UID, "Dinning Area", self.area, OpenSpaceType.DINNING_AREA) \
            .add_room(second_floor.UID, "library", self.area, RoomType.LIBRARY)

        self.assertEqual(len(building.get_floors()), 2)
        self.assertEqual(len(building.get_floor_by_number(1).get_rooms()), 1)
        self.assertEqual(len(building.get_floor_by_number(1).get_open_spaces()), 1)
        self.assertEqual(len(building.get_floor_by_number(2).get_rooms()), 1)
        self.assertEqual(len(building.get_floor_by_number(2).get_open_spaces()), 1)
        self.assertEqual(building.get_floor_by_number(1).get_open_space_by_name("Dinning Area").space_type,
                         OpenSpaceType.DINNING_AREA)
        self.assertEqual(building.get_floor_by_uid(second_floor.UID).get_room_by_name("library").area, self.area)

    def test_remove_open_space_to_building_floor(self):
        first_floor = Floor(self.floor_area, 1, FloorType.REGULAR, rooms=[self.room])
        second_floor = copy.deepcopy(first_floor)
        second_floor.number = 2
        second_floor.floor_type = FloorType.ROOFTOP
        second_floor.add_open_spaces([self.hall])
        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.RESIDENTIAL, [first_floor, second_floor])
        self.assertEqual(building.get_floor_by_number(2).get_open_spaces(), [self.hall])

        building.get_floor_by_number(2).remove_open_space(self.hall)
        self.assertEqual(building.get_floor_by_number(2).get_open_spaces(), [])
        self.assertEqual(building.get_floor_by_number(2).get_rooms(), [self.room])

    def test_building_with_no_operational_schedule(self):
        first_floor = Floor(self.floor_area, 1, FloorType.REGULAR, rooms=[self.room])
        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.RESIDENTIAL, [first_floor])
        self.assertEqual(building.schedulable_entity.get_schedules(), [])

    def test_add_operational_schedule_to_building(self):
        first_floor = Floor(self.floor_area, 1, FloorType.REGULAR, rooms=[self.room])
        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.RESIDENTIAL, [first_floor])
        schedule = OperationalSchedule("WEEKDAYS", datetime.now(), datetime.now() + timedelta(days=5))
        building.schedulable_entity.add_schedule(schedule)
        self.assertEqual(building.schedulable_entity.get_schedules(), [schedule])
        self.assertEqual(building.schedulable_entity.get_schedule_by_uid(schedule.UID).name, "WEEKDAYS")
        self.assertEqual(building.schedulable_entity.get_schedule_by_name(schedule.name).recurring, True)

    def test_add_building_floor_with_different_schedule(self):
        schedule = OperationalSchedule("WEEKDAYS", datetime.now(), datetime.now() + timedelta(days=5))
        floor_schedule = OperationalSchedule("WEEKEND", datetime.now(), datetime.now() + timedelta(days=2))
        self.building.schedulable_entity.add_schedule(schedule)
        self.building.get_floor_by_number(1).schedulable_entity.add_schedule(floor_schedule)
        self.assertEqual(self.building.schedulable_entity.get_schedules(), [schedule])
        self.assertEqual(self.building.get_floor_by_number(1).schedulable_entity.get_schedules(), [floor_schedule])
        self.assertNotEqual(self.building.schedulable_entity.get_schedules(),
                            self.building.get_floor_by_number(1).schedulable_entity.get_schedules())

    def test_remove_operational_schedule_to_building(self):
        first_floor = Floor(self.floor_area, 1, FloorType.REGULAR, rooms=[self.room])
        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.RESIDENTIAL, [first_floor])
        schedule = OperationalSchedule("WEEKDAYS", datetime.now(), datetime.now() + timedelta(days=5))
        building.schedulable_entity.add_schedule(schedule)
        self.assertEqual(building.schedulable_entity.get_schedules(), [schedule])

        building.schedulable_entity.remove_schedule(schedule)
        self.assertEqual(building.schedulable_entity.get_schedules(), [])
        self.assertEqual(len(building.schedulable_entity.get_schedules()), 0)

    def test_add_zone_to_building_and_floor(self):
        first_floor = Floor(self.floor_area, 1, FloorType.REGULAR, rooms=[self.room])
        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.RESIDENTIAL, [first_floor])
        zone = Zone("HVAC_COOLING_ZONE", ZoneType.HVAC, HVACType.PERIMETER)
        building.get_floor_by_uid(first_floor.UID).add_zone(zone, building)
        self.assertEqual(building.get_floor_by_number(1).get_zones(), [zone])
        self.assertEqual(building.get_zones(), [zone])
        self.assertEqual(building.get_zone_by_name(zone.name).get_spaces(), [first_floor])
        self.assertEqual(building.get_zone_by_name(zone.name).get_space_by_uid(first_floor.UID).get_zones(), [zone])

    def test_building_with_floors_in_different_zones(self):
        second_floor = Floor(self.floor_area, 2, FloorType.ROOFTOP, rooms=[self.room])
        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.RESIDENTIAL, [self.floor, second_floor])
        cooling_zone = Zone("HVAC_COOLING_ZONE", ZoneType.HVAC, HVACType.PERIMETER)
        heating_zone = Zone("HVAC_HEATING_ZONE", ZoneType.HVAC, HVACType.PERIMETER)

        building.get_floor_by_uid(self.floor.UID).add_zone(cooling_zone, building)
        building.get_floor_by_uid(second_floor.UID).add_zone(heating_zone, building)

        self.assertEqual(building.get_floor_by_uid(self.floor.UID).zones, [cooling_zone])
        self.assertEqual(building.get_floor_by_uid(second_floor.UID).zones, [heating_zone])
        self.assertEqual(building.zones, [cooling_zone, heating_zone])
        self.assertEqual(building.get_zone_by_name(cooling_zone.name).get_spaces(), [self.floor])
        self.assertEqual(building.get_zone_by_name(heating_zone.name).get_spaces(), [second_floor])

    def test_two_building_floors_with_same_zone(self):
        second_floor = Floor(self.floor_area, 2, FloorType.ROOFTOP, rooms=[self.room])
        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.RESIDENTIAL, [self.floor, second_floor])
        cooling_zone = Zone("HVAC_COOLING_ZONE", ZoneType.HVAC, HVACType.PERIMETER)
        building.get_floor_by_uid(self.floor.UID).add_zone(cooling_zone, building)
        building.get_floor_by_uid(second_floor.UID).add_zone(cooling_zone, building)

        self.assertEqual(building.zones, [cooling_zone])
        self.assertEqual(len(building.zones), 1)
        self.assertEqual(building.zones[0].name, "HVAC_COOLING_ZONE")
        self.assertEqual(building.get_floor_by_uid(self.floor.UID).zones, [cooling_zone])
        self.assertEqual(building.get_floor_by_uid(second_floor.UID).zones, [cooling_zone])
        self.assertEqual(building.zones[0].get_spaces(), [self.floor, second_floor])

    def test_two_building_floors_with_spaces_in_different_zones(self):
        second_floor = Floor(self.floor_area, 2, FloorType.ROOFTOP, open_spaces=[self.hall])
        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.RESIDENTIAL, [self.floor, second_floor])
        cooling_zone = Zone("HVAC_COOLING_ZONE", ZoneType.HVAC, HVACType.PERIMETER)
        heating_zone = Zone("HVAC_HEATING_ZONE", ZoneType.HVAC, HVACType.PERIMETER)
        lighting_zone = Zone("HVAC_LIGHTING_ZONE", ZoneType.LIGHTING)

        building.get_floor_by_number(1).get_room_by_name(self.room.name).add_zone(cooling_zone, building)
        building.get_floor_by_number(2).get_open_space_by_name(self.hall.name).add_zone(heating_zone, building)
        building.get_floor_by_number(1).add_zone(lighting_zone, building)

        self.assertEqual(len(building.zones), 3)
        self.assertEqual(building.zones, [cooling_zone, heating_zone, lighting_zone])
        self.assertEqual(
            building.get_floor_by_number(1).get_room_by_name(self.room.name).get_zone_by_name(cooling_zone.name),
            cooling_zone
        )
        self.assertEqual(
            building.get_floor_by_number(2).get_open_space_by_name(self.hall.name).get_zone_by_name(heating_zone.name),
            heating_zone
        )
        self.assertEqual(building.get_floor_by_number(1).get_zone_by_name(lighting_zone.name), lighting_zone)
        self.assertEqual(building.get_zone_by_name(cooling_zone.name).get_spaces(),
                         building.get_floor_by_number(1).get_rooms())
        self.assertEqual(building.get_zone_by_name(heating_zone.name).get_spaces(),
                         building.get_floor_by_number(2).get_open_spaces())

    def test_rooms_on_building_floor_in_adjacent_zones(self):
        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.RESIDENTIAL, [self.floor])
        building.get_floor_by_number(1).add_open_spaces([self.hall])
        cooling_zone = Zone("HVAC_COOLING_ZONE", ZoneType.HVAC, HVACType.PERIMETER)
        heating_zone = Zone("HVAC_HEATING_ZONE", ZoneType.HVAC, HVACType.PERIMETER)
        cooling_zone.add_adjacent_zones([heating_zone])
        building.get_floor_by_number(1).get_room_by_name(self.room.name).add_zone(cooling_zone, building)
        building.get_floor_by_number(1).get_open_space_by_name(self.hall.name).add_zone(heating_zone, building)
        self.assertEqual(building.zones, [cooling_zone, heating_zone])
        self.assertEqual(
            building.get_floor_by_number(1).get_room_by_name(self.room.name).get_zone_by_name(
                cooling_zone.name).get_adjacent_zones(),
            [heating_zone]
        )
        self.assertEqual(building.get_zone_by_name(cooling_zone.name).get_spaces(),
                         building.get_floor_by_number(1).get_rooms())

    def test_rooms_on_building_floor_in_overlapping_zones(self):
        building = Building(2009, self.height, self.floor_area, self.internal_mass, self.address,
                            BuildingType.RESIDENTIAL, [self.floor])
        building.get_floor_by_number(1).add_open_spaces([self.hall])
        cooling_zone = Zone("HVAC_COOLING_ZONE", ZoneType.HVAC, HVACType.PERIMETER)
        heating_zone = Zone("HVAC_HEATING_ZONE", ZoneType.HVAC, HVACType.PERIMETER)
        cooling_zone.add_overlapping_zones([heating_zone])
        building.get_floor_by_number(1).get_room_by_name(self.room.name).add_zone(cooling_zone, building)
        building.get_floor_by_number(1).get_open_space_by_name(self.hall.name).add_zone(heating_zone, building)
        self.assertEqual(building.zones, [cooling_zone, heating_zone])
        self.assertEqual(
            building.get_floor_by_number(1).get_room_by_name(self.room.name)
                .get_zone_by_name(cooling_zone.name).get_overlapping_zones(),
            [heating_zone]
        )
        self.assertEqual(building.get_zone_by_name(cooling_zone.name).get_spaces(),
                         building.get_floor_by_number(1).get_rooms())

    def test_remove_zone_from_building_floor(self):
        cooling_zone = Zone("HVAC_COOLING_ZONE", ZoneType.HVAC, HVACType.PERIMETER)
        self.building.get_floor_by_number(1).add_zone(cooling_zone, self.building)
        self.building.get_floor_by_number(1).remove_zone(cooling_zone)
        self.assertEqual(self.building.get_floor_by_number(1).get_zones(), [])
        self.assertEqual(self.building.get_zones(), [cooling_zone])
        self.assertEqual(self.building.get_zone_by_name(cooling_zone.name).get_spaces(), [])

    def test_add_meters_to_building(self):
        first_meter = Meter(meter_location="huz.cab.err",
                            manufacturer="Honeywell",
                            measurement_frequency=5,
                            measurement_unit=MeasurementUnit.KILOWATTS_PER_HOUR,
                            meter_type=MeterType.ELECTRICITY, measure_mode=MeterMeasureMode.AUTOMATIC)

        second_meter = Meter(meter_location="huz.cab.err",
                             manufacturer="Honeywell",
                             measurement_frequency=5,
                             measurement_unit=MeasurementUnit.KILOWATTS_PER_HOUR,
                             meter_type=MeterType.CHARGE_DISCHARGE, measure_mode=MeterMeasureMode.MANUAL)

        self.building.add_meter(first_meter)
        self.building.add_meter(second_meter)
        self.assertEqual(self.building.get_meters(), [first_meter, second_meter])
        self.assertEqual(self.building.get_meter_by_uid(first_meter.UID).meter_type, MeterType.ELECTRICITY)
        self.assertEqual(self.building.get_meter_by_uid(second_meter.UID).meter_type, MeterType.CHARGE_DISCHARGE)
        self.assertNotEqual(self.building.get_meter_by_uid(second_meter.UID), first_meter)

    def test_remove_meters_to_building(self):
        first_meter = Meter(meter_location="huz.cab.err",
                            manufacturer="Honeywell",
                            measurement_frequency=5,
                            measurement_unit=MeasurementUnit.KILOWATTS_PER_HOUR,
                            meter_type=MeterType.ELECTRICITY, measure_mode=MeterMeasureMode.AUTOMATIC)

        second_meter = Meter(meter_location="huz.cab.err",
                             manufacturer="Honeywell",
                             measurement_frequency=5,
                             measurement_unit=MeasurementUnit.KILOWATTS_PER_HOUR,
                             meter_type=MeterType.CHARGE_DISCHARGE, measure_mode=MeterMeasureMode.MANUAL)
        self.building.add_meter(first_meter)
        self.building.add_meter(second_meter)
        self.building.remove_meter(first_meter)

        self.assertEqual(self.building.get_meters(), [second_meter])
        self.assertEqual(self.building.get_meter_by_uid(second_meter.UID).meter_type, MeterType.CHARGE_DISCHARGE)

    def test_get_meter_by_uid(self):
        first_meter = Meter(meter_location="huz.cab.err",
                            manufacturer="Honeywell",
                            measurement_frequency=5,
                            measurement_unit=MeasurementUnit.KILOWATTS_PER_HOUR,
                            meter_type=MeterType.ELECTRICITY, measure_mode=MeterMeasureMode.AUTOMATIC)

        second_meter = Meter(meter_location="huz.cab.err",
                             manufacturer="Honeywell",
                             measurement_frequency=5,
                             measurement_unit=MeasurementUnit.KILOWATTS_PER_HOUR,
                             meter_type=MeterType.CHARGE_DISCHARGE, measure_mode=MeterMeasureMode.MANUAL)
        self.building.add_meter(first_meter)
        self.building.add_meter(second_meter)

        self.assertEqual(self.building.get_meter_by_uid(first_meter.UID), first_meter)

    def test_get_meter_by_type(self):
        first_meter = Meter(meter_location="huz.cab.err",
                            manufacturer="Honeywell",
                            measurement_frequency=5,
                            measurement_unit=MeasurementUnit.KILOWATTS_PER_HOUR,
                            meter_type=MeterType.ELECTRICITY, measure_mode=MeterMeasureMode.AUTOMATIC)

        second_meter = Meter(meter_location="huz.cab.err",
                             manufacturer="Honeywell",
                             measurement_frequency=5,
                             measurement_unit=MeasurementUnit.KILOWATTS_PER_HOUR,
                             meter_type=MeterType.CHARGE_DISCHARGE, measure_mode=MeterMeasureMode.MANUAL)
        self.building.add_meter(first_meter)
        self.building.add_meter(second_meter)
        self.assertEqual(self.building.get_meter_by_type(second_meter.meter_type.value), [second_meter])

    def test_search_meters(self):
        first_meter = Meter(meter_location="huz.cab.err",
                            manufacturer="Honeywell",
                            measurement_frequency=5,
                            measurement_unit=MeasurementUnit.KILOWATTS_PER_HOUR,
                            meter_type=MeterType.ELECTRICITY, measure_mode=MeterMeasureMode.AUTOMATIC)

        second_meter = Meter(meter_location="huz.cab.err",
                             manufacturer="Honeywell",
                             measurement_frequency=5,
                             measurement_unit=MeasurementUnit.KILOWATTS_PER_HOUR,
                             meter_type=MeterType.CHARGE_DISCHARGE, measure_mode=MeterMeasureMode.MANUAL)
        self.building.add_meter(first_meter)
        self.building.add_meter(second_meter)
        meters = self.building.get_meters({'manufacturer': 'Honeywell', 'meter_type': MeterType.ELECTRICITY.value})
        self.assertEqual(meters, [first_meter])

    def test_add_weather_stations_to_building(self):
        station_one = WeatherStation('Station One', location="huz.bob.cob")
        station_two = WeatherStation('Station Two', location="bob.cob.huz")
        self.building.add_weather_station(station_one)
        self.building.add_weather_station(station_two)
        self.assertEqual(self.building.get_weather_stations(), [station_one, station_two])
        self.assertEqual(self.building.get_weather_station_by_name(station_two.name).location, "bob.cob.huz")

    def test_get_weather_station_by_name(self):
        station_one = WeatherStation('Station One', location="huz.bob.cob")
        station_two = WeatherStation('Station Two', location="bob.cob.huz")
        self.building.add_weather_station(station_one)
        self.building.add_weather_station(station_two)

        station = self.building.get_weather_station_by_name(station_two.name)
        self.assertEqual(station_two, station)

    def test_get_weather_station_by_uid(self):
        station_one = WeatherStation('Station One', location="huz.bob.cob")
        station_two = WeatherStation('Station Two', location="bob.cob.huz")
        self.building.add_weather_station(station_one)
        self.building.add_weather_station(station_two)

        station = self.building.get_weather_station_by_uid(station_one.UID)
        self.assertEqual(station_one, station)

    def test_remove_weather_stations_to_building(self):
        station_one = WeatherStation('Station One', location="huz.bob.cob")
        station_two = WeatherStation('Station Two', location="bob.cob.huz")
        self.building.add_weather_station(station_one)
        self.building.add_weather_station(station_two)
        self.building.remove_weather_station(station_two)
        self.assertEqual(self.building.get_weather_stations(), [station_one])
        self.assertEqual(len(self.building.get_weather_stations()), 1)

    def test_add_envelop_to_building(self):
        cover = Cover(CoverType.ROOF)
        cover.add_layer(self.layer)
        new_layer = copy.deepcopy(self.layer)
        new_layer.has_vapour_barrier = True
        cover.add_layer(new_layer)
        envelope = Envelope()
        envelope.add_cover(cover)
        self.building.envelope = envelope
        self.assertEqual(self.building.envelope, envelope)
        self.assertEqual(self.building.envelope.get_cover_by_uid(cover.UID).cover_type, CoverType.ROOF)
        self.assertEqual(self.building.envelope.get_cover_by_uid(cover.UID).get_layers(), [self.layer, new_layer])
        self.assertEqual(self.building.envelope.get_cover_by_uid(cover.UID).get_layers()[0].thickness.value, 3)
        self.assertEqual(self.building.envelope.get_cover_by_uid(cover.UID).get_layers()[1].material.material_type,
                         MaterialType.ROOF_STEEL)

    def test_building_floor_area_change_history(self):
        structure_change_logger = StructureStateChangeLogger()
        self.building.track_state = True
        self.building.add_observer(structure_change_logger)
        self.building.floor_area = self.floor_area

        self.assertEqual(len(structure_change_logger.state_log), 1)
        self.assertEqual(structure_change_logger.state_log[0]['entity_type'], 'Building')
        self.assertEqual(structure_change_logger.state_log[0]['state']['floor_area'].value, self.floor_area.value)

    def test_building_weather_station_change_history(self):
        structure_change_logger = StructureStateChangeLogger()
        self.building.track_state = True
        self.building.add_observer(structure_change_logger)

        self.assertEqual(structure_change_logger.state_log, [])

        self.building.add_weather_station(WeatherStation('Station One', location="bob.cob.huz"))
        self.assertEqual(structure_change_logger.state_log[0]['state'], {'weather_stations': []})
        self.building.add_weather_station(WeatherStation('Station Two', location="zzz.cob.huz"))
        self.assertEqual(len(structure_change_logger.state_log), 2)
        self.assertEqual(structure_change_logger.state_log[1]['state']['weather_stations'][0].location, 'bob.cob.huz')

    def test_building_state_track_turned_off(self):
        structure_change_logger = StructureStateChangeLogger()
        self.building.track_state = False  # turn off tracking state changes
        self.building.add_observer(structure_change_logger)
        self.building.add_weather_station(WeatherStation('Station One', location="bob.cob.huz"))
        self.building.add_weather_station(WeatherStation('Station Two', location="zzz.cob.huz"))

        self.assertEqual(structure_change_logger.state_log, [])
