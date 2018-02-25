#!/usr/bin/env python3
## https://gist.github.com/Uberi/283a13b8a71a46fb4dc8
 
import time, random
import math
from collections import deque

start = time.time()

class RealtimePlot:
    def __init__(self, axes, max_entries = 1000000):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.axes = axes
        self.max_entries = max_entries
        
        self.lineplot, = axes.plot([], [], "ro-")
        self.axes.set_autoscaley_on(True)

    def add(self, x, y):
        self.axis_x.append(x)
        self.axis_y.append(y)
        self.lineplot.set_data(self.axis_x, self.axis_y)
        self.axes.set_xlim(self.axis_x[0], self.axis_x[-1] + 1e-15)
        self.axes.relim(); self.axes.autoscale_view() # rescale the y-axis

    def animate(self, figure, callback, interval = 50):
        import matplotlib.animation as animation
        def wrapper(frame_index):
            self.add(*callback(frame_index))
            self.axes.relim(); self.axes.autoscale_view() # rescale the y-axis
            return self.lineplot
        animation.FuncAnimation(figure, wrapper, interval=interval)

def main():
    from matplotlib import pyplot as plt

    fibonacci_numbers = [0, 1]
    for i in range(2,700):
        fibonacci_numbers.append(fibonacci_numbers[i-1]+fibonacci_numbers[i-2])
    
    fig, [ax1, ax2] = plt.subplots(nrows=1, ncols=2, sharey=False)
    plt.tight_layout()
    display1 = RealtimePlot(ax1, max_entries=15)
    display2 = RealtimePlot(ax2)
    #while True:
    for j in range(50):
        display1.add(time.time() - start, fibonacci_numbers[j])
        display2.add(time.time() - start, fibonacci_numbers[j])
        plt.pause(0.1)

    return display2, plt.pause(10), plt.close('all')
    

if __name__ == "__main__":
    a = main()
    ## returns list of measurements and timings 
    #TODO: select boxID being selenised, autosaves copy to box folder. save 
