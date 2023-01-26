#Source
import plotly.graph_objects as go
import pandas as pd
from scipy.signal import find_peaks

#from detecta import detect_peaks
from scipy.signal import find_peaks


def Find_Peaks(df,ColName):

    TimeStamp_PV=[] # Time stamps of peaks and valleys
    SignalValue_PV=[] # Signal Values of peaks and valleys
    Label_PV=[] # Label of peaks(1) and valleys(-1)
    
    num=0
    INDEX=[]
    skip=[]
    i=0
    
    resp_dt=df['TimeStamp'].tolist()

    #Peak Detection
    resp_sig = df[ColName].tolist()
    index = find_peaks(resp_sig,height=20)[0]
   
    #Finding minima between peaks to find valleys
    while(i<len(index)-1):
        diff_bet_peaks=resp_sig[index[i]]-resp_sig[index[i+1]]
        if((diff_bet_peaks<0) & ((resp_sig[index[i]]-(min(resp_sig[index[i]:index[i+1]])))<5)):
            i=i+1
            continue
            
        SignalValue_PV.append(resp_sig[index[i]])
        TimeStamp_PV.append(resp_dt[index[i]])
        
        Label_PV.append(1)
        
        INDEX.append(index[i])
        
        #Valleys Detection
        if(i<len(index)-2):
            seg_valley_val=min(resp_sig[index[i]:index[i+1]])
            seg_valley_index = resp_sig.index(seg_valley_val,index[i],index[i+1])
            hts=resp_sig[index[i+1]]-seg_valley_val
            diff=resp_sig[index[i+1]]-(min(resp_sig[index[i]:index[i+1]]))
            if ((i>0)& ((resp_sig[index[i+1]]-(min(resp_sig[index[i]:index[i+1]])))<5)):
                #resp_sig[index[i]]-(min(resp_sig[index[i]:index[i+2]]))<5
                j=i
                while(((resp_sig[index[j+1]]-(min(resp_sig[index[j]:index[j+1]])))<5) and (j<len(index)-3)):
                    j=j+1
                if (j<len(index)-2):
                    j=j+1
                
                seg_valley_val=min(resp_sig[index[j-1]:index[j]])
                seg_valley_index = resp_sig.index(seg_valley_val,index[j-1],index[j])
                INDEX.append(seg_valley_index)
                SignalValue_PV.append(seg_valley_val)
                TimeStamp_PV.append(resp_dt[seg_valley_index])
                Label_PV.append(-1)
                
                #i=i+2
                i=j
                continue
                
            INDEX.append(seg_valley_index)
            SignalValue_PV.append(seg_valley_val)
            TimeStamp_PV.append(resp_dt[seg_valley_index])
            Label_PV.append(-1)
            #skip[i]=0
        i=i+1
        
        
    d = {'Label_PV':Label_PV,\
        'SignalValue_PV':SignalValue_PV,\
         'TimeStamp_PV':TimeStamp_PV,
        'INDEX':INDEX}
 
    Res_scipy = pd.DataFrame(d)
    return(Res_scipy)
