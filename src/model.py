import mesa
try:
    from mesa.space import SingleGrid
except ImportError:
    raise ImportError("Failed to import SingleGrid from mesa.space. Ensure Mesa version >=2.1.0 is installed.")
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from src.agents import ReservoirAgent
from src.constants import STEAM_INJECTION_RATE, STEAM_TEMP

class ReservoirModel(mesa.Model):
    def __init__(self, width=20, height=20):
        super().__init__()
        self.grid = SingleGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.injection_well = (width // 2, height - 1)  # Bottom center
        self.production_well = (width // 2, height - 3)  # Near injection well
        self.total_oil_produced = 0.0
        self.total_steam_injected = 0.0
        self.steam_temp = STEAM_TEMP

        # Create agents (grid blocks)
        for i in range(width):
            for j in range(height):
                agent = ReservoirAgent((i, j), self, (i, j))
                self.grid.place_agent(agent, (i, j))
                self.schedule.add(agent)

        # Data collector for metrics
        self.datacollector = DataCollector(
            model_reporters={
                "Oil Produced": "total_oil_produced",
                "SOR": lambda m: m.total_steam_injected / max(m.total_oil_produced, 1e-6)
            },
            agent_reporters={"Oil Saturation": "oil_saturation", "Temperature": "temperature"}
        )

    def step(self):
        # Inject steam at injection well
        injection_agent = self.grid.get_cell_list_contents([self.injection_well])[0]
        self.total_steam_injected += STEAM_INJECTION_RATE * injection_agent.porosity
        self.schedule.step()
        self.datacollector.collect(self)