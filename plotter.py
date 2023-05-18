from histogrammer import *
from df_toolkit import *
from cut import *



if __name__ == "__main__":
    file = '/home/alconley/Projects/Data/WorkingDir/built/run_291.parquet'

    df = pl.read_parquet(file)
    
    
    CutXColumn="ScintLeftEnergy"
    CutYColumn="AnodeBackEnergy"
    Cut_df = df.select([CutXColumn,CutYColumn]).filter((pl.col(CutXColumn) != -1e6) & (pl.col(CutYColumn) != -1e6))
    
    draw_cut(df=Cut_df, XColumn=CutXColumn, XParameters=[256,0,2048], YColumn=CutYColumn, YParameters=[256,0,2048], OutputFile="cut_run_291_ScintLeft_AnodeBack.json")

    