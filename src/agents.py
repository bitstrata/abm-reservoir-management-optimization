import mesa
import numpy as np
from src.constants import (
    POROSITY, PERMEABILITY, INITIAL_OIL_SAT, INITIAL_WATER_SAT,
    RESERVOIR_TEMP, BITUMEN_VISCOSITY, VISCOSITY_TEMP_COEFF, STEAM_INJECTION_RATE
)

class ReservoirAgent(mesa.Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
        self.porosity = POROSITY * np.random.uniform(0.9, 1.1)  # Slight variation
        self.permeability = PERMEABILITY * np.random.uniform(0.8, 1.2)
        self.oil_saturation = INITIAL_OIL_SAT
        self.water_saturation = INITIAL_WATER_SAT
        self.temperature = RESERVOIR_TEMP
        self.steam_saturation = 0.0
        self.pressure = 1000  # kPa, initial reservoir pressure

    def calculate_viscosity(self):
        # Bitumen viscosity decreases with temperature
        return BITUMEN_VISCOSITY * np.exp(VISCOSITY_TEMP_COEFF * (self.temperature - RESERVOIR_TEMP))

    def step(self):
        # Receive steam/heat from injection or neighbors
        if self.pos == self.model.injection_well:
            self.steam_saturation += STEAM_INJECTION_RATE * self.porosity
            self.temperature += (self.model.steam_temp - self.temperature) * 0.5  # Simplified heat transfer
            self.water_saturation = max(0, self.water_saturation - STEAM_INJECTION_RATE)
            self.oil_saturation = max(0, self.oil_saturation - STEAM_INJECTION_RATE)

        # Interact with neighbors (fluid flow and heat transfer)
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        for neighbor in neighbors:
            neighbor = self.model.grid.get_cell_list_contents([neighbor])[0]
            # Fluid flow (simplified Darcy's law)
            flow_rate = (self.permeability * (self.pressure - neighbor.pressure) / self.calculate_viscosity()) * 0.01
            if flow_rate > 0:
                oil_transfer = min(self.oil_saturation, flow_rate * self.porosity)
                self.oil_saturation -= oil_transfer
                neighbor.oil_saturation += oil_transfer
                neighbor.water_saturation = max(0, neighbor.water_saturation - oil_transfer)
            # Heat transfer
            temp_diff = self.temperature - neighbor.temperature
            neighbor.temperature += temp_diff * 0.1  # Simplified conduction

        # Update pressure based on fluid content
        self.pressure = 1000 + 500 * (self.oil_saturation + self.steam_saturation)

        # Produce oil if near production well
        if self.pos == self.model.production_well:
            produced_oil = min(self.oil_saturation, 0.05 * self.porosity)  # Simplified production
            self.oil_saturation -= produced_oil
            self.model.total_oil_produced += produced_oil
            self.water_saturation = max(0, self.water_saturation - produced_oil)

        # Ensure saturations sum to 1
        total_sat = self.oil_saturation + self.water_saturation + self.steam_saturation
        if total_sat > 1:
            self.oil_saturation /= total_sat
            self.water_saturation /= total_sat
            self.steam_saturation /= total_sat