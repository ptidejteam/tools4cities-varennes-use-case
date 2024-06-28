import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname("."), '..')))

from building_structure.structure import Structure
from pathlib import Path
from metamenth.measure_instruments.weather_station import WeatherStation
import sys
from metamenth.datatypes.zone import Zone
from metamenth.enumerations import ZoneType
from metamenth.enumerations import HVACType
from metamenth.enumerations import SensorMeasure
from metamenth.enumerations import MeasurementUnit
from metamenth.enumerations import SensorMeasureType
from metamenth.enumerations import SensorLogType
from metamenth.transducers.sensor import Sensor
from building_structure.dynamic_data import DynamicData
from metamenth.measure_instruments.meter import Meter
from metamenth.enumerations import MeterType
from metamenth.enumerations import MeterMeasureMode


class VarennesLibrary:
    def __init__(self):
        self.structure = Structure()
        # load building structural json data
        path = Path(__file__).resolve().parent.parent / 'building_structure/data/building.json'
        self.structure.load_building_data(path)
        self.dynamic_data = DynamicData()
        self.building = None

    def create_building(self):
        """
        Creates the building with floors, rooms, open spaces and sensors
        :return:
        """
        try:
            first_floor = self.structure.building_data["building"]["floors"][0]
            first_room = first_floor["rooms"][0]

            room = self.structure.create_room(first_room["name"], first_room['area'], first_room['room_type'], None)

            floor = self.structure.create_floor(first_floor["area"], first_floor["number"], first_floor["floor_type"],
                                                [room], [])

            building_data = self.structure.building_data["building"]

            self.building = self.structure.create_building(building_data["construction_year"], building_data["height"],
                                                           building_data['floor_area'], building_data['internal_mass'],
                                                           building_data['address'], building_data['building_type'],
                                                           [floor])

            floor.add_rooms(self._add_spaces(first_floor['rooms'])) \
                .add_open_spaces(self._add_spaces(first_floor['open_spaces']))

            weather_station = WeatherStation('Weather Station',
                                             location=building_data['address']['what3word'])
            # add weather station
            self.building.add_weather_station(weather_station)

            # add meter
            self._add_meter()

            # add all floors
            self._populate_floors(building_data["floors"])
            self.__add_zones()
        except KeyError as err:
            print(err, file=sys.stderr)

    def _populate_floors(self, floor_data):
        """
        create floors from json data
        :param floor_data: json data of floors
        :return:
        """
        building_floors = []
        for floor_data in floor_data:
            first_room = floor_data['rooms'][0]
            first_room = self.structure.create_room(first_room["name"], first_room['area'],
                                                    first_room['room_type'], None)
            floor = self.structure.create_floor(floor_data["area"], floor_data["number"],
                                                floor_data["floor_type"], [first_room], [])

            floor.add_rooms(self._add_spaces(floor_data['rooms']))
            floor.add_open_spaces(self._add_spaces(floor_data['open_spaces']))

            building_floors.append(floor)
        self.building.add_floors(building_floors)

    def _add_spaces(self, spaces):
        """
        creates rooms and open spaces from json data
        :param spaces: the space json data
        :return:
        """
        # add open spaces to the floor
        new_spaces = []
        for space in spaces:
            if 'room_type' in space:
                new_space = self.structure.create_room(space["name"], space['area'],
                                                       space['room_type'], None)
            else:
                new_space = self.structure.create_open_space(space["name"],
                                                             space['area'],
                                                             space['space_type'], None)
            # add sensors
            self._add_sensors(space['sensors'], new_space)
            new_spaces.append(new_space)
        return new_spaces

    def __add_zones(self):
        floor_number = 0
        for space in self.structure.building_data["building"]["floors"]:
            for room in space['rooms']:

                for zone_name in room['zones']:
                    room_obj = self.building.get_floor_by_number(floor_number).get_room_by_name(room['name'])
                    existing_zone = self.building.get_zone_by_name(zone_name)
                    new_zone = existing_zone if existing_zone else Zone(zone_name, ZoneType.HVAC, HVACType.INTERIOR)
                    room_obj.add_zone(new_zone, self.building)

            for open_space in space['open_spaces']:
                for zone_name in open_space['zones']:
                    open_space_obj = self.building.get_floor_by_number(floor_number).get_open_space_by_name(open_space['name'])
                    open_space_obj.add_zone(Zone(zone_name, ZoneType.HVAC, HVACType.INTERIOR), self.building)
            floor_number += 1

    def _add_sensors(self, sensors, space):
        """
        Creates sensors from json data
        :param sensors: the json sensor data
        :param space: the space (room or open space) which the sensor
        is created for
        :return:
        """
        for sensor in sensors:
            space.add_transducer(Sensor(sensor['name'], SensorMeasure.get_enum_type(sensor['measure']),
                                        MeasurementUnit.get_enum_type(sensor['unit']),
                                        SensorMeasureType.THERMO_COUPLE_TYPE_A,
                                        sensor['data_frequency'],
                                        sensor_log_type=SensorLogType.get_enum_type(sensor['log_type'])))

    def _add_meter(self):
        """
        Adds meter to the building
        :return:
        """

        building_data = self.structure.building_data['building']
        meter_data = building_data['meter']
        meter = Meter(meter_location=building_data['address']['what3word'], manufacturer=meter_data['manufacturer'],
                      measurement_frequency=meter_data['data_frequency'],
                      measurement_unit=MeasurementUnit.get_enum_type(meter_data['unit']),
                      meter_type=MeterType.get_enum_type(meter_data['type']),
                      measure_mode=MeterMeasureMode.get_enum_type(meter_data['measure_mode']))
        self.building.add_meter(meter)

    def add_sensor_data(self):
        """
        Populate space sensors with data
        :return:
        """
        for floor in self.building.get_floors():
            for room in floor.get_rooms():
                self.dynamic_data.add_sensor_data(room)

            for open_space in floor.get_open_spaces():
                self.dynamic_data.add_sensor_data(open_space)

    def add_weather_station_data(self):
        """
        add weather station data
        :return:
        """
        self.dynamic_data.add_weather_data(self.building.get_weather_station_by_name('Weather Station'))

    def add_meter_electricity_consumption_data(self):
        self.dynamic_data.add_electricity_consumption_data(self.building.get_meter_by_type(MeterType.ELECTRICITY.value)[0])
