import matplotlib.pyplot as plt
import numpy as np
import io

def plot_data():
    t = np.arange(0.0, 2.0, 0.01)
    s = 1 + np.sin(2*np.pi*t)
    plt.plot(t, s)
    plot_io = io.BytesIO()
    plt.savefig(plot_io)
    return plot_io  