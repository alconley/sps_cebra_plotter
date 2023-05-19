'''
This a just histogram class with the settings I like to use.

For 1d histograms I also allow you display stats like mean, stdev, and Intergral.  This also updates when you zoom in (like ROOT lol)

To call this, 
    import histogrammer
    
    histogrammer.histo1d(variables)
'''


import polars as pl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors


class histogrammer:
    def __init__(self, df: pl.DataFrame):
        self.df = df
    
    def histo1d(self, column: str, x_parameters:list, ax:plt.Axes=None, label=None, display_stats=None):
        
        if ax == None:
            fig, ax = plt.subplots(1,1)
        else:
            fig = ax.figure
           
        bins, initial, final = x_parameters
        counts, bins, _ = ax.hist(self.df[column], bins=bins, range=(initial, final), histtype='step', label=label)
        ax.set_xlim(initial,final)
        ax.set_xlabel(column)
        ax.set_ylabel("Counts")
        if label is not None:
            ax.legend(loc='upper left')
        ax.minorticks_on()
        ax.tick_params(axis='both', which='minor', direction='in', top=True, right=True, left=True, bottom=True, length=2)
        ax.tick_params(axis='both', which='major', direction='in', top=True, right=True, left=True, bottom=True, length=5)
    
        if display_stats == True:
            data = np.array(self.df[column])
            bin_width = bins[1] - bins[0]
            bin_indices = np.digitize(data, bins) - 1
            data_in_range = data[(data >= initial) & (data <= final)]
            
            integral = np.sum(counts) * bin_width
            mean = np.average(data_in_range)
            std_dev = np.std(data_in_range)
            
            text_box = ax.text(0.95, 0.85, f"Integral: {integral:.2f}\nMean: {mean:.2f}\nStd Dev: {std_dev:.2f}",
                            transform=ax.transAxes, verticalalignment='top', horizontalalignment='right',
                            bbox={'facecolor': 'white', 'alpha': 0.8, 'pad': 5, 'edgecolor': 'none'})
            
            def update_stats(event):
                if ax.get_xlim() == (initial, final):
                    return
                
                xlim = ax.get_xlim()
                data_in_range = data[(data >= xlim[0]) & (data <= xlim[1])]
                integral = np.sum(counts[(bins[:-1] >= xlim[0]) & (bins[1:] <= xlim[1])]) * bin_width
                mean = np.average(data_in_range)
                std_dev = np.std(data_in_range)
                
                text_box.set_text(f"Integral: {integral:.2f}\nMean: {mean:.2f}\nStd Dev: {std_dev:.2f}")
                ax.figure.canvas.draw()
                
            ax.callbacks.connect('xlim_changed', update_stats)
        
        
        return fig
    
    def histo2d(self, x_column: str, x_parameters: list, y_column: str, y_parameters: list, ax:plt.Axes=None):
        
        if ax == None:
            fig, ax = plt.subplots(1,1)
        else:
            fig = ax.figure
    
        x_bins, x_initial, x_final = x_parameters
        y_bins, y_initial, y_final = y_parameters
        ax.hist2d(self.df[x_column], self.df[y_column], bins=[x_bins, y_bins],range=[[x_initial, x_final], [y_initial, y_final]], norm=colors.LogNorm())
        ax.set_xlim(x_initial,x_final)
        ax.set_ylim(y_initial,y_final)
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)
        ax.minorticks_on()
        ax.tick_params(axis='both', which='minor', direction='in', top=True, right=True, left=True, bottom=True, length=2)
        ax.tick_params(axis='both', which='major', direction='in', top=True, right=True, left=True, bottom=True, length=5)
        
        return fig