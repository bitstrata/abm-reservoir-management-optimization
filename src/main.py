from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import Grid
import numpy as np

class ReservoirAgent(Agent):
    def __init__(self, unique_id, model, pressure=100, production_rate=0.1):
        super().__init__(unique_id, model)
        self.pressure = pressure  # Reservoir pressure (example property)
        self.production_rate = production_rate  # Production rate (bbl/day)

    def step(self):
        # Simulate production and pressure decline
        self.pressure -= self.production_rate * 0.05  # Simplified decline
        if self.pressure < 10:
            self.production_rate = 0  # Stop production if pressure too low

class ReservoirManagementModel(Model):
    def __init__(self, N, width, height, max_production_rate=0.2):
        self.num_agents = N
        self.grid = Grid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.max_production_rate = max_production_rate

        # Place agents (e.g., wells or reservoir units)
        for i in range(self.num_agents):
            pressure = np.random.uniform(50, 150)  # Random initial pressure
            production_rate = np.random.uniform(0, max_production_rate)
            agent = ReservoirAgent(i, self, pressure, production_rate)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)

    def step(self):
        # Optimize production (e.g., adjust rates to maximize total output)
        total_production = sum(agent.production_rate for agent in self.schedule.agents)
        for agent in self.schedule.agents:
            # Example optimization: reduce rate if pressure is low
            if agent.pressure < 50 and agent.production_rate > 0:
                agent.production_rate *= 0.9
        self.schedule.step()
        return total_production

if __name__ == "__main__":
    model = ReservoirManagementModel(10, 10, 10)
    for i in range(10):
        total_production = model.step()
        print(f"Step {i+1}: Total Production = {total_production:.2f} bbl/day")