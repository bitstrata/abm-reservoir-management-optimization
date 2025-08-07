from src.model import ReservoirModel
from src.visualization import plot_simulation_results

def run_simulation(steps=100):
    model = ReservoirModel()
    for i in range(steps):
        model.step()
    plot_simulation_results(model, steps)

if __name__ == "__main__":
    run_simulation(steps=100)