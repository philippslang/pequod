import matplotlib.pyplot as plt
import numpy as np
import io

def plot_data():
    t = np.arange(0.0, 2.0, 0.01)
    s = 1 + np.sin(2*np.pi*t)
    plt.plot(t, s)
    plt.grid(True)
    io_buffer = io.BytesIO()
    plt.savefig(io_buffer)
    return io_buffer  