#from ExtractFeatures import Calculate_B_2_B_Features
import pandas as pd
import numpy as np
import uuid
import time
import random
from multiprocessing import Pool, Manager
from .FeatureExtractor import Calculate_B_2_B_Features


import multiprocessing

done_tasks = []


def on_task_done(results):
    done_tasks.append(results)

def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


#Function to get the arguments for the package and give messages if the requuired argument is provided or not
def RespFeatureExtract(**kwargs):
    GetFeatures=pd.DataFrame()
    if 'PV' not in kwargs:
        print("PV is a required parameter.")
        exit(0)
    elif 'PV' in kwargs:
        if(len(kwargs['PV'])==0):
            print("PV is a required parameter and dataframe is empty.")
            exit(0)
        
    elif 'Sig_val_Col' not in kwargs:
        print("Sig_val_Col is a required parameter.")
    
    elif 'Peak_Valley_Label' not in kwargs:
        print("Peak_Valley_Label is a required parameter.")
        
    elif 'timestamp_col' not in kwargs:
        print("timestamp_col is a required parameter.")
    
    if 'cpu_cores' not in kwargs:
        #Setting cpu_cores as 1 if the value is not provided by the users
        kwargs['cpu_cores']=1
    if 'cpu_cores' in kwargs:
        #print("cpu_cores",kwargs['cpu_cores'])
        if kwargs['cpu_cores'] > multiprocessing.cpu_count():
            print("You have provided more cores than your machine can support ",multiprocessing.cpu_count())
            Core=multiprocessing.cpu_count()-1
    
    if 'window' not in kwargs:
        #print("Sig_val_Col is a required parameter.")
        kwargs['window']=60
    
    GetFeatures=MainProcessCall(kwargs['PV'],kwargs['Sig_val_Col'],kwargs['timestamp_col'],kwargs['Peak_Valley_Label'],kwargs['window'],kwargs['cpu_cores'])
    
    return(GetFeatures)


#Function Call which segments the data in to multiple windows of fixed length time as provided by the user.
def MainProcessCall(df,Signal,Time,Label_peakval,WindowSize,Core):
    df[Time] = pd.to_datetime(df[Time])
    
    #Getting the min and max of the timestamps in the data
    minTime=df[Time].min()
    maxTime=df[Time].max()
    
    #Getting the maximum time in seconds and dividing it by the the fixed length window time provided by the user to segment the data.
    timedelta = pd.Timedelta(df[Time].max()-df[Time].min()).total_seconds()
    NumCycles=timedelta/WindowSize
    
    # Multiprocessing in segmenting the data and extracting the features.
    m = Manager()
    procs = m.dict()
    pool = Pool(processes=Core) # Number of CPUs
    start=df[Time].min()
    Features=[]
    for x in range(int(NumCycles)): #<Number of Time Windows>
        end=pd.to_datetime(start + pd.to_timedelta(int(WindowSize), unit='s'))
        sub_Signal=df[(df[Time] >= start) & (df[Time]<=end)]
        
        if sub_Signal.shape[0]>0:
            #print("Sirst",type(start),type(end))
            results=pool.apply_async(Calculate_B_2_B_Features, args=(sub_Signal,Signal,Time,Label_peakval,), callback=on_task_done) #Each Window Start and End, Signal segmentation and feature extraction parallely 
            start=end
        else:
            #print("tirst",type(start),type(end))
            continue
    
    pool.close()
    pool.join()
    
    #print("###################")
    #print('results:', done_tasks) #Convert Done tasks into the pandas dataframe. Return would be pandas dataframe
    #print("###################")
    
    column_name=['Start','End','RMSSD','MDI','MADI','RespRate','RMS_DA','RMI','BPI']
    df_write = pd.DataFrame (done_tasks, columns = column_name)
    #print(df_write.head())
    #df_write.to_csv("TestResultRespFeaturesMulti.csv",index=False)
    return(df_write)
