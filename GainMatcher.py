'''
In an ideal world, this python file will not be used.

In the CeBrA demostrator, the peak positions moved over time. This was due to the source being unsteady and the rate caused the PMTs to shift the peaks.

Therefore I had to "Gain Match" the detectors.  Luckly, there were many background peaks so for every run and for every detector I fit guassians to every peak in the background spectrum.  
    Note that using background peaks is not ideal in case there is a doppler shift.  But my stats were low.
    
I then extracted all this information and basically preformmed a 2nd order calibration to the first run. i.e. plot first_run vs run and fit a polynomial to it.

With this information, I created a new column "Cebra{det_num}Energy_GainMatched".  This column now allows me to add all the runs together and to view the spectrum.
    
This file is going to assume that the data was fitted using HDTV and the user saved the fit files for each detector and run

Note that I had to fit like 5000 guassians, so I recommend using a scriptting program like HDTV for this
'''

import xml.etree.ElementTree as ET
import numpy as np
from scipy.optimize import curve_fit
import polars as pl
import os

#For parsing the HDTV XML Fit File
def general_xml(file: str):
    mytree = ET.parse(file)
    myroot = mytree.getroot()
 
    uncal_fit_list = []
    uncal_fit_err_list = []
    uncal_width_list = []
    uncal_width_err_list = []
    uncal_volume_list = []
    uncal_volume_err_list = []

    cal_fit_list = []
    cal_fit_err_list = []
    cal_width_list = []
    cal_width_err_list = []
    cal_volume_list = []
    cal_volume_err_list = []

    for fit in myroot:
        for i in fit:
            if i.tag == 'peak':
                for child in i.iter():
                    if child.tag == 'uncal':
                        for j in child.iter():
                            if j.tag == 'pos':
                                for newchild in j.iter():
                                    if newchild.tag == 'value':
                                        fit_value = newchild.text
                                        uncal_fit_list.append(float(fit_value))
                                    elif newchild.tag == 'error':
                                        fit_err = newchild.text
                                        uncal_fit_err_list.append(float(fit_err))
                            elif j.tag == 'vol':
                                for newchild in j.iter():
                                    if newchild.tag == 'value':
                                        vol_value = newchild.text
                                        uncal_volume_list.append(float(vol_value))
                                    elif newchild.tag == 'error':
                                        vol_err = newchild.text
                                        uncal_volume_err_list.append(float(vol_err))
                            elif j.tag == 'width':
                                for newchild in j.iter():
                                    if newchild.tag == 'value':
                                        width_value = newchild.text
                                        uncal_width_list.append(float(width_value))
                                    elif newchild.tag == 'error':
                                        width_err = newchild.text
                                        uncal_width_err_list.append(float(width_err))

                    #gets the calibrated data information                
                    if child.tag == 'cal':
                        for j in child.iter():
                            if j.tag == 'pos':
                                for newchild in j.iter():
                                    if newchild.tag == 'value':
                                        fit_value = newchild.text
                                        cal_fit_list.append(float(fit_value))
                                    elif newchild.tag == 'error':
                                        fit_err = newchild.text
                                        cal_fit_err_list.append(float(fit_err))
                            elif j.tag == 'vol':
                                for newchild in j.iter():
                                    if newchild.tag == 'value':
                                        vol_value = newchild.text
                                        cal_volume_list.append(float(vol_value))
                                    elif newchild.tag == 'error':
                                        vol_err = newchild.text
                                        cal_volume_err_list.append(float(vol_err))
                            elif j.tag == 'width':
                                for newchild in j.iter():
                                    if newchild.tag == 'value':
                                        width_value = newchild.text
                                        cal_width_list.append(float(width_value))
                                    elif newchild.tag == 'error':
                                        width_err = newchild.text
                                        cal_width_err_list.append(float(width_err))
    
    # uncalibrated data handling
    uncal_list = []
    for val in zip(uncal_fit_list, uncal_fit_err_list, uncal_width_list, uncal_width_err_list, uncal_volume_list, uncal_volume_err_list):  #interleaves lists together
        uncal_list.append(val)
    sorted_uncal_list = sorted(uncal_list, reverse=True)

    # calibrated data handling
    cal_list = []
    for val in zip(cal_fit_list, cal_fit_err_list, cal_width_list, cal_width_err_list, cal_volume_list, cal_volume_err_list):  #interleaves lists together
        cal_list.append(val)
    sorted_cal_list = sorted(cal_list, reverse=True)

    return sorted_uncal_list, sorted_cal_list

#Takes the general_xml file and returns the position and position uncertainity
def hdtv_fit_to_pos_values(file: str):
    
    uncal_list, cal_list = general_xml(file)

    fit_paramaters = []
    position = []
    for i in range(len(uncal_list)):
        pos = cal_list[i][0]
        pos_err = cal_list[i][1]
        FWHM = cal_list[i][2]
        FWHM_err = cal_list[i][3]
        volume = cal_list[i][4]
        volume_err = cal_list[i][5]


        hdtv_fit = [pos, pos_err]
        fit_paramaters.append(hdtv_fit)

    return fit_paramaters

def GainMatchCalibrationRetriever(InitialRunFitFile: str, RunFitFile: str):

    #49Ti
    # path = "./cebraE_Raw_Gain_Matching/fits/"
    # filename for 49Ti=  det_{Det_Number}_spectrum_{i}.fit
    
    def poly1(x, m, b):
        return m*x + b

    def poly2(x, a, b, c):
        return a*x*x + b*x + c

    calibration_peaks = hdtv_fit_to_pos_values(InitialRunFitFile)

    pos = np.array([])
    pos_err = np.array([])
    for i in range(len(calibration_peaks)):
        pos = np.append(pos,calibration_peaks[i][0])
        pos_err = np.append(pos_err,calibration_peaks[i][1])

    fit = hdtv_fit_to_pos_values(RunFitFile)

    pos_fit = np.array([])
    pos_err_fit = np.array([])
    for i in range(len(fit)):
        pos_fit = np.append(pos_fit, fit[i][0])
        pos_err_fit = np.append(pos_err_fit, fit[i][1])

    popt, pcov = curve_fit(poly2, pos_fit, pos, sigma=pos_err_fit, absolute_sigma=True)
    
    GainMatchCalibrationValues = popt
    return GainMatchCalibrationValues
    
'''
I am now going to read in a built .parquet file and create a copy of the Cebra0Energy to a column called Cebra0EnergyRaw.  

Then I am going to apply the calibration from the GainMatchCalibrationRetriever to this column.This will the for the other detectors.
'''

#Creates a list of run numbers given the path and how the built files should look. 
# Directory should only have the good runs in it.
WorkingDirPath = "/home/alconley/Projects/Data/WorkingDir/"

RunList = []
for filename in os.listdir(f"{WorkingDirPath}built/"):
    if filename.endswith(".parquet"):
        run_number = int(filename.split("_")[1].split(".")[0])
        RunList.append(run_number)

RunList.sort()
print(f"Using runs: {RunList}")

for Run in RunList:
    
    print(f"Gain Matching Run: {Run}")
    
    # Read in the run dataframe file
    df = pl.read_parquet(f"{WorkingDirPath}built/run_{Run}.parquet")
    
    for DetectorNumber in range(5):
        
        # This is the file structure to the first run that all my detectors will be shifted to, i.e. Run 291.
        InitialRunFitFile = f"/home/alconley/Projects/CeBrA_Analysis/61Ni/all_61Ni_CeBrA_Fits/det_{DetectorNumber}/cebraE{DetectorNumber}_fits/291_det_{DetectorNumber}.fit"
        
        # This is the file path that we will get the calibration values for
        RunFitFile = f"/home/alconley/Projects/CeBrA_Analysis/61Ni/all_61Ni_CeBrA_Fits/det_{DetectorNumber}/cebraE{DetectorNumber}_fits/{Run}_det_{DetectorNumber}.fit"
        
        # Get the calibtration values from the function created above
        GainMatchedCalibrationValues = GainMatchCalibrationRetriever(InitialRunFitFile, RunFitFile)

        # Creates a copy of the column for each detector.
        df = df.with_columns( pl.col(f"Cebra{DetectorNumber}Energy").alias(f"Cebra{DetectorNumber}EnergyRaw"))

        # apply the gain matching calibration values to the dataframe
        df = df.with_columns( ( (GainMatchedCalibrationValues[0]*pl.col(f"Cebra{DetectorNumber}Energy")*pl.col(f"Cebra{DetectorNumber}Energy")) + (GainMatchedCalibrationValues[1]*pl.col(f"Cebra{DetectorNumber}Energy")) + (GainMatchedCalibrationValues[2]) ).alias(f"Cebra{DetectorNumber}Energy"))

    # Created a new directory to put the gainmatched dataframe files in
    # You could overwrite the original but I do not like to mess with them.
    OutputDataframeFile = f"/home/alconley/Projects/Data/WorkingDir/built_gainmatched/run_{Run}.parquet"
    
    df.write_parquet(OutputDataframeFile) # write the dataframe to a parquet file

