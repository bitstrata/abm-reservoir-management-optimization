import unittest
from src.agents import ReservoirAgent
from src.model import ReservoirModel

class TestReservoirAgent(unittest.TestCase):
    def setUp(self):
        self.model = ReservoirModel(width=5, height=5)
        self.agent = ReservoirAgent(unique_id=(0, 0), model=self.model, pos=(0, 0))

    def test_calculate_viscosity(self):
        # Test viscosity at initial temperature
        expected_viscosity = 1000000  # BITUMEN_VISCOSITY at RESERVOIR_TEMP
        self.assertAlmostEqual(self.agent.calculate_viscosity(), expected_viscosity, places=2)

        # Test viscosity after temperature increase
        self.agent.temperature = 50
        expected_viscosity = 1000000 * np.exp(-0.05 * (50 - 10))
        self.assertAlmostEqual(self.agent.calculate_viscosity(), expected_viscosity, places=2)

if __name__ == "__main__":
    unittest.main()