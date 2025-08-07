import mesa
import logging
try:
    from mesa.space import SingleGrid
except ImportError:
    raise ImportError("Failed to import SingleGrid from mesa.space. Ensure Mesa version >=2.1.0 is installed.")
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from src.agents import ReservoirAgent
from src.constants import STEAM_INJECTION_RATE, STEAM_TEMP

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReservoirModel(mesa.Model):
    def __init__(self, width=20, height=20):
        super().__init__()
        self.grid = SingleGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.injection_well_row = height - 1  # Horizontal well along bottom row
        self.production_well_row = height - 3  # Horizontal well two rows above
        self.total_oil_produced = 0.0
        self.total_steam_injected = 0.0
        self.steam_temp = STEAM_TEMP

        # Track used positions to prevent duplicates
        used_positions = set()

        # Clear grid to ensure no residual agents
        for pos in self.grid.coord_iter():
            pos = pos[1]  # Get (x, y) tuple
            if not self.grid.is_cell_empty(pos):
                for agent in self.grid.get_cell_list_contents([pos]):
                    self.grid.remove_agent(agent)
                    self.schedule.remove(agent)

        # Create and place agents with unique IDs
        agent_id = 0
        for i in range(width):
            for j in range(height):
                pos = (i, j)
                if pos in used_positions:
                    logger.error(f"Attempting to place agent at already used position {pos}")
                    continue
                if not self.grid.is_cell_empty(pos):
                    logger.error(f"Cell {pos} is unexpectedly occupied before placement.")
                    continue
                agent = ReservoirAgent(unique_id=agent_id, model=self, pos=pos)
                logger.debug(f"Placing agent {agent_id} at {pos}")
                self.grid.place_agent(agent, pos)
                self.schedule.add(agent)
                used_positions.add(pos)
                agent_id += 1
                if j == self.injection_well_row:
                    logger.debug(f"Placed injection well agent {agent_id} at {pos}")
                elif j == self.production_well_row:
                    logger.debug(f"Placed production well agent {agent_id} at {pos}")

        # Verify grid state
        for i in range(width):
            for j in range(height):
                contents = self.grid.get_cell_list_contents([(i, j)])
                if len(contents) != 1:
                    logger.error(f"Cell {(i, j)} has {len(contents)} agents: {contents}")

        # Data collector for metrics
        self.datacollector = DataCollector(
            model_reporters={
                "Oil Produced": "total_oil_produced",
                "SOR": lambda m: m.total_steam_injected / max(m.total_oil_produced, 1e-6)
            },
            agent_reporters={"Oil Saturation": "oil_saturation", "Temperature": "temperature"}
        )

    def step(self):
        # Inject steam along the entire injection well row
        for i in range(self.grid.width):
            pos = (i, self.injection_well_row)
            injection_agent = self.grid.get_cell_list_contents([pos])[0]
            self.total_steam_injected += STEAM_INJECTION_RATE * injection_agent.porosity
        self.schedule.step()
        self.datacollector.collect(self)