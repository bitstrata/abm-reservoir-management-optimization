import unittest
import numpy as np
from src.agents import ReservoirAgent
from src.model import ReservoirModel

class TestReservoirAgent(unittest.TestCase):
    def setUp(self):
        self.model = ReservoirModel(width=5, height=5)
        self.agent = ReservoirAgent(unique_id=0, model=self.model, pos=(0, 0))

    def test_calculate_viscosity(self):
        # Test viscosity at initial temperature
        expected_viscosity = 1000000  # BITUMEN_VISCOSITY at RESERVOIR_TEMP
        self.assertAlmostEqual(self.agent.calculate_viscosity(), expected_viscosity, places=2)

        # Test viscosity after temperature increase
        self.agent.temperature = 50
        expected_viscosity = 1000000 * np.exp(-0.05 * (50 - 10))
        self.assertAlmostEqual(self.agent.calculate_viscosity(), expected_viscosity, places=2)

    def test_initial_conditions(self):
        # Test randomized initial conditions
        self.assertTrue(0.1 <= self.agent.porosity <= 0.4, "Porosity out of range")
        self.assertTrue(500 <= self.agent.permeability <= 1500, "Permeability out of range")
        self.assertTrue(0.5 <= self.agent.oil_saturation <= 0.9, "Oil saturation out of range")
        self.assertTrue(0.1 <= self.agent.water_saturation <= 0.3, "Water saturation out of range")
        self.assertAlmostEqual(
            self.agent.oil_saturation + self.agent.water_saturation + self.agent.steam_saturation,
            1.0, places=2, msg="Saturations do not sum to 1"
        )

if __name__ == "__main__":
    unittest.main()