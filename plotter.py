from histogrammer import *
from df_toolkit import *
from cut import load_cut_json, write_cut_json, CutHandler, draw_cut
from cmath import pi
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


WorkingDirPath = "/home/alconley/Projects/Data/WorkingDir/"

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

def PlotManyFigures(figs):
    # Create a Tkinter window
    root = tk.Tk()
    root.title("SPS Plotter")

    # Set the window size
    window_width = root.winfo_screenwidth()
    window_height = root.winfo_screenheight()
    root.geometry(f"{window_width}x{window_height}")

    # Create a main frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Create a canvas for the main frame
    canvas = tk.Canvas(main_frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create a scrollbar for the main frame
    scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a horizontal scrollbar for the main frame
    x_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=canvas.xview)
    x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    canvas.configure(xscrollcommand=x_scrollbar.set)

    # Create a scrollable frame within the canvas
    scrollable_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)

    # Configure the scrollable frame to expand with the window
    scrollable_frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))

    # Define the number of columns and desired plots per row
    num_columns = 3
    plots_per_row = 3

    # Create a counter to keep track of the current plot
    plot_counter = 0

    for fig in figs:
        # Calculate the row and column for the current plot
        row = plot_counter // plots_per_row
        column = plot_counter % num_columns

        # Create a frame for the figure
        figure_frame = ttk.Frame(scrollable_frame)
        figure_frame.grid(row=row, column=column, padx=10, pady=10)

        # Create a canvas for the figure
        figure_canvas = FigureCanvasTkAgg(fig, master=figure_frame)
        figure_canvas.draw()
        figure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create a toolbar for the figure
        toolbar = NavigationToolbar2Tk(figure_canvas, figure_frame)
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.BOTH)

        # Close the figure
        plt.close()
        
        # Increment the plot counter
        plot_counter += 1

    # Update the canvas scrollable region
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

    # Bind mousewheel events to the canvas
    canvas.bind("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
    canvas.bind("<Shift-MouseWheel>", lambda event: canvas.xview_scroll(int(-1 * (event.delta / 120)), "units"))

    # Run the Tkinter event loop
    root.mainloop()


def SPSPlotter(df: pl.DataFrame, Cut: str = None, CutXColumn: str = None, CutYColumn: str = None):

    if Cut is not None:
        if CutXColumn is None or CutYColumn is None:
            raise ValueError("Both CutXColumn and CutYColumn must be provided when Cut is not None.")

        cut = load_cut_json(Cut)
        
        df = df.filter(pl.col(CutXColumn).arr.concat(CutYColumn).map(cut.is_cols_inside))


    # Declare new columns that could be used with the just the SPS
    df = df.with_columns( [ ((pl.col(f"DelayBackRightEnergy") + pl.col("DelayBackLeftEnergy"))/2).alias(f"DelayBackAvgEnergy"),\
                            ((pl.col(f"DelayFrontRightEnergy") + pl.col("DelayFrontLeftEnergy"))/2).alias(f"DelayFrontAvgEnergy"),\
                            (pl.col(f"DelayFrontLeftTime") - pl.col("AnodeFrontTime")).alias(f"DelayFrontLeftTime_AnodeFrontTime"),\
                            (pl.col(f"DelayFrontRightTime") - pl.col("AnodeFrontTime")).alias(f"DelayFrontRightTime_AnodeFrontTime"),\
                            (pl.col(f"DelayBackLeftTime") - pl.col("AnodeFrontTime")).alias( f"DelayBackLeftTime_AnodeFrontTime"),\
                            (pl.col(f"DelayBackRightTime") - pl.col("AnodeFrontTime")).alias(f"DelayBackRightTime_AnodeFrontTime"),\
                            (pl.col(f"DelayFrontLeftTime") -  pl.col("AnodeBackTime")).alias(f"DelayFrontLeftTime_AnodeBackTime"),\
                            (pl.col(f"DelayFrontRightTime") - pl.col("AnodeBackTime")).alias(f"DelayFrontRightTime_AnodeBackTime"),\
                            (pl.col(f"DelayBackLeftTime") -   pl.col("AnodeBackTime")).alias(f"DelayBackLeftTime_AnodeBackTime"),\
                            (pl.col(f"DelayBackRightTime") -  pl.col("AnodeBackTime")).alias(f"DelayBackRightTime_AnodeBackTime"),\
                            (pl.col(f"AnodeFrontTime") - pl.col("AnodeBackTime")).alias(f"AnodeFrontTime_AnodeBackTime"),\
                            (pl.col(f"AnodeBackTime") - pl.col("ScintLeftTime")).alias(f"AnodeBackTime_ScintLeftTime"),\
                            (pl.col(f"AnodeFrontTime") - pl.col("ScintLeftTime")).alias(f"AnodeFrontTime_ScintLeftTime"),\
                            (pl.col(f"DelayFrontLeftTime") -  pl.col("ScintLeftTime")).alias(f"DelayFrontLeftTime_ScintLeftTime"),\
                            (pl.col(f"DelayFrontRightTime") - pl.col("ScintLeftTime")).alias(f"DelayFrontRightTime_ScintLeftTime"),\
                            (pl.col(f"DelayBackLeftTime") -  pl.col("ScintLeftTime")).alias(f"DelayBackLeftTime_ScintLeftTime"),\
                            (pl.col(f"DelayBackRightTime") - pl.col("ScintLeftTime")).alias(f"DelayBackRightTime_ScintLeftTime")])
        
    # Timing realtive to back anode columns
    df_time_relative_back_anode = df.filter((pl.col("AnodeBackTime") != -1) & (pl.col("ScintLeftTime") != -1))

    df_no_x2 = df.filter((pl.col("X1") != -1e6) & (pl.col("X2") == -1e6))
    df_no_x1 = df.filter((pl.col("X1") == -1e6) & (pl.col("X2") != -1e6))
    df_bothplanes = df.filter((pl.col("X1") != -1e6) & (pl.col("X2") != -1e6))
    
    hg = histogrammer(df)           
    hg_no_x2 = histogrammer(df_no_x2)
    hg_no_x1 = histogrammer(df_no_x1)
    hg_bothplanes = histogrammer(df_bothplanes)
    
    
    figs = []
    
    figs.append(hg.histo2d("ScintLeftEnergy",[512,0,4096],"AnodeBackEnergy", [512,0,4096]))
    figs.append(hg.histo2d("ScintLeftEnergy",[512,0,4096],"AnodeFrontEnergy",[512,0,4096]))
    figs.append(hg.histo2d("ScintLeftEnergy",[512,0,4096],"CathodeEnergy",[512,0,4096]))
    
    figs.append(hg.histo1d("Xavg",[600,-300,300],display_stats=True))
    figs.append(hg.histo2d("X1",[600,-300,300],"X2", [600,-300,300]))
    figs.append(hg.histo2d("Xavg",[600,-300,300],"Theta", [600,0,pi/2]))
    
    figs.append(hg.histo2d("X1",    [600,-300,300],"AnodeBackEnergy",[512,0,4096]))
    figs.append(hg.histo2d("X2",    [600,-300,300],"AnodeBackEnergy",[512,0,4096]))
    figs.append(hg.histo2d("Xavg",  [600,-300,300],"AnodeBackEnergy",[512,0,4096]))
    
    figs.append(hg.histo2d("X1",    [600,-300,300],"AnodeFrontEnergy",[512,0,4096]))
    figs.append(hg.histo2d("X2",    [600,-300,300],"AnodeFrontEnergy",[512,0,4096]))
    figs.append(hg.histo2d("Xavg",  [600,-300,300],"AnodeFrontEnergy",[512,0,4096]))
    
    figs.append(hg.histo2d("X1",    [600,-300,300],"CathodeEnergy",[512,0,4096]))
    figs.append(hg.histo2d("X2",    [600,-300,300],"CathodeEnergy",[512,0,4096]))
    figs.append(hg.histo2d("Xavg",  [600,-300,300],"CathodeEnergy",[512,0,4096]))
    
    fig_x1, ax_x1 = plt.subplots(1,1)
    hg_bothplanes.histo1d("X1",[600,-300,300], label='x1: bothplanes',ax=ax_x1)
    hg_no_x2.histo1d("X1",[600,-300,300], label='x1: no x2',ax=ax_x1)
    figs.append(fig_x1)
    
    fig_x2, ax_x2 = plt.subplots(1,1)
    hg_bothplanes.histo1d("X2",[600,-300,300],label='x2: bothplanes',ax=ax_x2)
    hg_no_x1.histo1d("X2",[600,-300,300],label='x2: no x1',ax=ax_x2)
    figs.append(fig_x2)
        
    figs.append(hg_bothplanes.histo1d("Xavg",[600,-300,300],display_stats=True))
    
    figs.append(hg.histo2d("X1",[600,-300,300],"DelayBackRightEnergy",[512,0,4096]))
    figs.append(hg.histo2d("X2",[600,-300,300],"DelayBackRightEnergy",[512,0,4096]))
    figs.append(hg.histo2d("Xavg",[600,-300,300],"DelayBackRightEnergy",[512,0,4096]))
    figs.append(hg.histo2d("X1",[600,-300,300],"DelayBackAvgEnergy",[512,0,4096]))
    figs.append(hg.histo2d("X2",[600,-300,300],"DelayBackAvgEnergy",[512,0,4096]))
    figs.append(hg.histo2d("Xavg",[600,-300,300],"DelayBackAvgEnergy",[512,0,4096]))
    figs.append(hg.histo2d("X1",[600,-300,300],"DelayFrontAvgEnergy",[512,0,4096]))
    figs.append(hg.histo2d("X2",[600,-300,300],"DelayFrontAvgEnergy",[512,0,4096]))
    figs.append(hg.histo2d("Xavg",[600,-300,300],"DelayFrontAvgEnergy",[512,0,4096]))

    PlotManyFigures(figs)

if __name__ == "__main__":
    
    file = '/home/alconley/Projects/Data/WorkingDir/built/run_291.parquet'

    df = pl.read_parquet(file)
    
    # Cut_df = df.select(["ScintLeftEnergy","AnodeBackEnergy"]).filter((pl.col("ScintLeftEnergy") != -1e6) & (pl.col("AnodeBackEnergy") != -1e6))
    # draw_cut(df=Cut_df, XColumn="ScintLeftEnergy", XParameters=[256,0,2048], YColumn="AnodeBackEnergy", YParameters=[256,0,2048], OutputFile="cut_run_291_ScintLeft_AnodeBack.json")

    SPSPlotter(df=df,Cut="cut_run_291_ScintLeft_AnodeBack.json",CutXColumn="ScintLeftEnergy", CutYColumn="AnodeBackEnergy")