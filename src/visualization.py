import numpy as np
import matplotlib.pyplot as plt

def plot_simulation_results(model, steps):
    # Collect data for visualization
    oil_saturation = np.zeros((model.grid.width, model.grid.height))
    temperature = np.zeros((model.grid.width, model.grid.height))
    for cell in model.grid.coord_iter():
        agent, pos = cell
        oil_saturation[pos[0], pos[1]] = agent.oil_saturation
        temperature[pos[0], pos[1]] = agent.temperature

    # Plot oil saturation and temperature
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(oil_saturation, cmap="viridis", origin="lower")
    plt.colorbar(label="Oil Saturation")
    plt.title(f"Oil Saturation at Step {steps}")
    plt.subplot(1, 2, 2)
    plt.imshow(temperature, cmap="hot", origin="lower")
    plt.colorbar(label="Temperature (°C)")
    plt.title(f"Temperature at Step {steps}")
    plt.tight_layout()
    plt.savefig("reservoir_output.png")
    plt.close()

    # Plot production metrics
    data = model.datacollector.get_model_vars_dataframe()
    plt.figure(figsize=(10, 5))
    plt.plot(data["Oil Produced"], label="Cumulative Oil Produced")
    plt.plot(data["SOR"], label="Steam-to-Oil Ratio")
    plt.xlabel("Step")
    plt.ylabel("Value")
    plt.legend()
    plt.title("Production Metrics")
    plt.savefig("production_metrics.png")
    plt.close()