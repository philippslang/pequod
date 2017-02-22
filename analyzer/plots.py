import matplotlib.pyplot as plt
import io

# An object for handling plots

class Plot():
    def __init__(self):
        self._x = None
        self._y = None
        self._title = ''
        self._xlabel = 'Time (DAYS)'
        self._ylabel = ''
        
    def setXData(self, data, label='Time (DAYS)'):
        self._x = data
        self._label = label
        
    def setYData(self, data, label=''):
        self._y = data
        self._ylabel = label
    
    def setTitle(self, title):
        self._title = title
    
    def getPlotImage(self):
        plt.cla()
        plt.plot(self._x, self._y)
        plt.xlabel(self._xlabel)
        plt.ylabel(self._ylabel)
        plt.title(self._title)
        plt.grid('on')
        plot_io = io.BytesIO()
        plt.savefig(plot_io)
        return plot_io  
