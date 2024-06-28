import json
import sys
from metamenth.structure.floor import Floor
from metamenth.structure.room import Room
from metamenth.structure.open_space import OpenSpace
from metamenth.datatypes.binary_measure import BinaryMeasure
from metamenth.datatypes.measure import Measure
from metamenth.enumerations import MeasurementUnit
from metamenth.enumerations import FloorType
from metamenth.enumerations import RoomType
from metamenth.enumerations import OpenSpaceType
from metamenth.structure.building import Building
from metamenth.datatypes.address import Address
from metamenth.datatypes.point import Point
from metamenth.enumerations import BuildingType


class Structure:
    def __init__(self):
        self._building_data = None

    @property
    def building_data(self):
        return self._building_data

    def load_building_data(self, file_path):
        try:
            with open(file_path, 'r') as file:
                self._building_data = json.load(file)
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.", file=sys.stderr)

    def create_floor(self, area: {}, floor_number: int, floor_type: str, rooms: [Room], open_spaces: [OpenSpace]) -> Floor:
        area = BinaryMeasure(self._create_measure(area))
        floor_type = FloorType.get_enum_type(self._get_proper_case(floor_type))
        return Floor(area, floor_number, floor_type, open_spaces=open_spaces, rooms=rooms)

    def create_room(self, name: str, area: {}, room_type: str, location: str = None) -> Room:
        room_type = RoomType.get_enum_type(self._get_proper_case(room_type))
        area = BinaryMeasure(self._create_measure(area))
        return Room(area, name, room_type, location)

    def create_open_space(self, name: str, area: {}, space_type: str, location: str = None) -> OpenSpace:
        area = BinaryMeasure(self._create_measure(area))
        space_type = OpenSpaceType.get_enum_type(self._get_proper_case(space_type))
        return OpenSpace(name, area, space_type, location)

    def create_building(self, construction_year: int, height: {}, floor_area: {}, internal_mass: {}, address: {},
                        building_type: str, floors: [Floor]) -> Building:
        b_height = BinaryMeasure(self._create_measure(height))
        b_floor_area = BinaryMeasure(self._create_measure(floor_area))
        b_internal_mass = BinaryMeasure(self._create_measure(internal_mass))
        b_address = Address(
            address['city'],
            address['street'],
            address['state'],
            address['zip_code'],
            address['country'],
            Point(address['coordinates']['longitude'], address['coordinates']['latitude']))
        return Building(construction_year, b_height, b_floor_area, b_internal_mass, b_address,
                        BuildingType.get_enum_type(building_type), floors)

    def _create_measure(self, area: {}):
        unit = MeasurementUnit.get_enum_type(area["unit"])
        return Measure(unit, area["value"])

    def _get_proper_case(self, input_string: str):
        words = input_string.replace('-', ' ').split()
        # Capitalize each word and join them without spaces
        formatted_string = ''.join(word.capitalize() for word in words)
        return formatted_string
