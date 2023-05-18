import polars as pl
from cut import *

def reducer(Cut: str, XColumnCut: str, YColumnCut: str, File: str, Output: str):
    
    df = pl.read_parquet(File) # read in the temporary dataframe from the parquet file

    cut = load_cut_json(Cut) # load the cut
    
    df = df.filter(pl.col(XColumnCut).arr.concat(YColumnCut).map(cut.is_cols_inside)) # filters the data with the cut
    
    df.write_parquet(Output) # write the dataframe to a parquet file
    
    
'''
To combine dataframes

df = pl.concat(dfs,how="vertical") # concatenate the list of dataframes into a single dataframe

where dfs is a list of a bunch of polars dataframes
'''
