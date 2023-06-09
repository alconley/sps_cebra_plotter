from matplotlib.path import Path
from polars import Series
import numpy as np
from typing import Optional
from numpy.typing import ArrayLike
import json
import polars as pl
import polars as pl
import matplotlib.pyplot as plt
from matplotlib import pyplot, widgets, colors

"""
Handler to recieve vertices from a matplotlib selector (i.e. PolygonSelector).
Typically will be used interactively, most likely via cmd line interpreter. The onselect
method should be passed to the selector object at construction. CutHandler can also be used in analysis
applications to store cuts.

Example:

from evbutils import CutHandler, Cut2D, write_cut_json
from matplotlib.widgets import PolygonSelector
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1,1)
handler = CutHandler()
selector = PolygonSelector(ax, handler.onselect)

--- plot some data ---

plt.show()

--- draw your cut on the plot and then close the plot window ---

mycut = handler.cuts["cut_0"]
mycut.name = "mycut"
write_cut_json(mycut, "mycut.json")

"""
class CutHandler:
    def __init__(self):
        self.cuts: dict[str, Cut2D] = {}

    def onselect(self, vertices: list[tuple[float, float]]):
        cut_default_name = f"cut_{len(self.cuts)}"
        self.cuts[cut_default_name] = Cut2D(cut_default_name, vertices)
"""
Implementation of 2D cuts as used in many types of graphical analyses with matplotlib
Path objects. Takes in a name (to identify the cut) and a list of points. The Path
takes the verticies, and can then be used to check if a point(s) is inside of the polygon using the 
is_*_inside functions. Can be serialized to json format. Can also retreive Nx2 ndarray of vertices
for plotting after the fact.
"""
class Cut2D:
    def __init__(self, name: str, vertices: list[tuple[float, float]]):
        self.path: Path = Path(vertices, closed=True)
        self.name = name
        
    def is_point_inside(self, x: float, y: float) -> bool:
        return self.path.contains_point((x,  y))

    def is_arr_inside(self, points: list[tuple[float, float]]) -> list[bool]:
        return self.path.contains_points(points)

    def is_cols_inside(self, columns: Series) -> Series:
        return Series(values=self.path.contains_points(columns.to_list()))

    def get_vertices(self) -> np.ndarray:
        return self.path.vertices

    def to_json_str(self) -> str:
        return json.dumps(self, default=lambda obj: {"name": obj.name, "vertices": obj.path.vertices.tolist()} )

def write_cut_json(cut: Cut2D, filepath: str) -> bool:
    json_str = cut.to_json_str()
    try:
        with open(filepath, "w") as output:
            output.write(json_str)
            return True
    except OSError as error:
        print(f"An error occurred writing cut {cut.name} to file {filepath}: {error}")
        return False

def load_cut_json(filepath: str) -> Optional[Cut2D]:
    try:
        with open(filepath, "r") as input:
            buffer = input.read()
            cut_dict = json.loads(buffer)
            if not "name" in cut_dict or not "vertices" in cut_dict:
                print(f"Data in file {filepath} is not the right format for Cut2D, could not load")
                return None
            return Cut2D(cut_dict["name"], cut_dict["vertices"])
    except OSError as error:
        print(f"An error occurred reading trying to read a cut from file {filepath}: {error}")
        return None



'''
This draws the cut

You have to give the function

1) The polars dataframe
    so read in the parquet file like:
        df = pl.read_parquet(f'path/run_{RUNNO}.parquet')
        it is best if you filter the dataframe first, i.e. Basic Energy Filter: df = df.filter((pl.col(XColumn) != -1e6) & (pl.col(YColumn) != -1e6))
2) The x-column name as a string
3) The x-column parameters as a list in the format [bins,initial,final]
4) The y-column name as a string
5) The y-column parameters as a list in the format [bins,initial,final]
6) Cut output file, i.e. 'path/name.json'

'''

def draw_cut(df:pl.DataFrame, XColumn:str, XParameters:list, YColumn:str, YParameters:list, OutputFile: str):
    
    handler = CutHandler()
    fig, ax = pyplot.subplots(1,1)

    x_bins,x_initial,x_final = XParameters
    y_bins,y_initial,y_final = YParameters
    
    selector = widgets.PolygonSelector(ax, handler.onselect)

    ax.hist2d(df.select(XColumn).to_series(), df.select(YColumn).to_series(), [x_bins,y_bins], [[x_initial, x_final],[y_initial,y_final]],norm=colors.LogNorm())

    plt.show(block=True)
    
    handler.cuts["cut_0"].name = "cut"
    write_cut_json(handler.cuts["cut_0"], OutputFile)
    
    
    
    '''
    To read the cut and filter a dataframe use
        
    cut = load_cut_json(f"{cut_name}")
    
    # Filter the df with cut
    df = df.filter(pl.col(XColumn).arr.concat(YColumn).map(cut.is_cols_inside))
    
    '''