from unittest import TestCase
from metamenth.enumerations import MaterialType
from metamenth.structure.material import Material
from metamenth.misc import MeasureFactory
from metamenth.enumerations import RecordingType
from metamenth.datatypes.measure import Measure
from metamenth.enumerations import MeasurementUnit


class TestMaterial(TestCase):

    def setUp(self) -> None:
        self.density_measure = MeasureFactory.create_measure(RecordingType.BINARY.value,
                                                             Measure(MeasurementUnit.KILOGRAM_PER_CUBIC_METER, 0.5))
        self.hc_measure = MeasureFactory.create_measure(RecordingType.BINARY.value,
                                                        Measure(MeasurementUnit.JOULES_PER_KELVIN, 4.5))
        self.tt_measure = MeasureFactory.create_measure(RecordingType.BINARY.value,
                                                        Measure(MeasurementUnit.WATTS_PER_SQUARE_METER_KELVIN, 2.5))
        self.material = None

    def test_material_without_thermal_resistance(self):
        try:
            self.material = Material(
                description="Material for the external wall of a building_structure",
                material_type=MaterialType.EX_WALL_BRICK,
                density=self.density_measure,
                heat_capacity=self.hc_measure,
                thermal_transmittance=self.tt_measure
            )
        except TypeError as err:
            self.assertEqual(err.__str__(), "__init__() missing 1 required positional argument: 'thermal_resistance'")

    def test_valid_material(self):

        tr_measure = MeasureFactory.create_measure(RecordingType.BINARY.value,
                                                        Measure(MeasurementUnit.SQUARE_METERS_KELVIN_PER_WATTS,
                                                                2.3))
        self.material = Material(
            description="Material for the external wall of a building_structure",
            material_type=MaterialType.EX_WALL_BRICK,
            density=self.density_measure,
            heat_capacity=self.hc_measure,
            thermal_transmittance=self.tt_measure,
            thermal_resistance=tr_measure
        )
        # Test UID is not empty and that it's generated automatically
        self.assertTrue(self.material.UID)

        # Test other attributes
        self.assertEqual(self.material.thermal_transmittance, self.tt_measure)
        self.assertEqual(self.material.material_type, MaterialType.EX_WALL_BRICK)
        self.assertEqual(self.material.thermal_resistance, tr_measure)

    def test_material_with_none_thermal_resistance(self):
        try:
            self.material = Material(
                description="Material for the external wall of a building_structure",
                material_type=MaterialType.EX_WALL_BRICK,
                density=self.density_measure,
                heat_capacity=self.hc_measure,
                thermal_transmittance=self.tt_measure,
                thermal_resistance=None
            )

        except ValueError as err:
            self.assertEqual(err.__str__(), "thermal_resistance is/are mandatory")
