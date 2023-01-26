import numpy as np
import pandas as pd
import statistics
import math


def variance(RespiratoryRate):
    mean=RespiratoryRate
    x=16
    deviations = (x - mean) ** 2
    variance = deviations / 1
    return variance
 
def stdev(RespiratoryRate):
    import math
    var = variance(RespiratoryRate)
    std_dev = math.sqrt(var)
    return std_dev


#Consider 2 peaks at a time for the caclulations
def RespFeatureExtractFromSingleWindow(**kwargs):
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
        
    
    GetFeatures=Calculate_B_2_B_Features(kwargs['PV'],kwargs['Sig_val_Col'],kwargs['timestamp_col'],kwargs['Peak_Valley_Label'])
    
    return(GetFeatures)


def Calculate_B_2_B_Features(data,Signal,Time,Label_peakval):
    
    #print("Entered",data,Signal,Time,Label_peakval)
    
    data[Time] = pd.to_datetime(data[Time])
    minTime=data[Time].min()
    maxTime=data[Time].max()
    
    #print(minTime,maxTime)
    
    i=0
    Resp_Cycle=1
    
    #OutputFromFindPeaks
    r_pvs = data[Label_peakval].to_list() # peak or valley (-1 or 1)
    r_vals = data[Signal].to_list() # value of peaks or valleys amplitude
    r_time = data[Time].to_list() # time at peaks and valleys
    
    #Things To be Calculated
    Diff_IE=[]
    count=[]
    Start=[]
    End=[]
    Breath_to_Breath=[] 
    SD_B2B_Inter=[] #successive differences of breath-to-breath intervals
    Sucessive_BtoB_diffenceInAmplitudes=[] # Difference between amplitudes of two sucessive peaks 2nd-1st.
    #Note: Difference between amplitudes of two sucessive valleys is calculated from 
   
    I_inter=[]
    E_inter=[]
    
    Ai_inter=[]
    Ae_inter=[]
    ht_max=[]
    ht_mean=[]
    A_inter=[]
    
    #Looping through peaks(1) and valleys(-1)
    while(i<data.shape[0]-9):
        
        #CASE 1: Starting with a valley
        if((r_pvs[i]==-1) and r_pvs[i+1]==1 and r_pvs[i+2]==-1 and r_pvs[i+3]==1):     
            
            #the inspiration and expiration intervals
            I_inter.append((r_time[i+1]-r_time[i]).total_seconds())
            I_inter.append((r_time[i+3]-r_time[i+2]).total_seconds())
            
            E_inter.append((r_time[i+2]-r_time[i+1]).total_seconds())
            if(r_pvs[i+4]==-1):
                E_inter.append((r_time[i+4]-r_time[i+3]).total_seconds())
            else:
                E_inter.append(math.nan)
                
            # The differences of the amplitudes of peaks and valleys for inspiration and expiration are defined as:
            Ai_inter.append(r_vals[i+1]-r_vals[i]) #peaksAmplitudes(P1) - valleyAmplitudes(V1)
            A_inter.append(r_vals[i+1]-r_vals[i])
            
            Ae_inter.append(r_vals[i+1]-r_vals[i+2])#peaks Amplitudes(P1) - valleyAmplitudes(V2)
            A_inter.append(r_vals[i+1]-r_vals[i+2])
            
            Ai_inter.append(r_vals[i+3]-r_vals[i+2])
            A_inter.append(r_vals[i+3]-r_vals[i+2])
            
            maxi_Amp=max(r_vals[i],r_vals[i+2])
            mean_Amp=np.mean([r_vals[i],r_vals[i+2]])
            
            ht_max.append(r_vals[i+1]-maxi_Amp)
            ht_mean.append(r_vals[i+1]-mean_Amp)
            
            if(r_pvs[i+4]==-1):
                Ae_inter.append(r_vals[i+3]-r_vals[i+4])
                A_inter.append(r_vals[i+3]-r_vals[i+4])
                
                maxi_Amp=max(r_vals[i+2],r_vals[i+4])
                mean_Amp=np.mean([r_vals[i+2],r_vals[i+4]])
            
                ht_max.append(r_vals[i+3]-maxi_Amp)
                ht_mean.append(r_vals[i+3]-mean_Amp)
                
            else:
                Ae_inter.append(math.nan)
                A_inter.append(math.nan)
                
                ht_max.append(r_vals[i+3]-r_vals[i+2])
                ht_mean.append(r_vals[i+3]-r_vals[i+2])
      
            # Starts Breath to breath intervals
            B2B_Inter_1=(r_time[i+3]-r_time[i+1]).total_seconds() #Breath to breath intervals (Peak to peak)
            
            if((r_pvs[i+4]==-1) and r_pvs[i+5]==1 and r_pvs[i+6]==-1 and r_pvs[i+7]==1):
                B2B_Inter_2=(r_time[i+7]-r_time[i+5]).total_seconds()
                Diff=abs(B2B_Inter_2-B2B_Inter_1)
                SD_B2B_Inter.append(Diff) #successive differences of breath-to-breath(peak to peak) intervals
            else:
                SD_B2B_Inter.append(math.nan)
            
            # Ends Breath to breath intervals   
            Breath_to_Breath.append((r_time[i+3]-r_time[i+1]).total_seconds())
            Sucessive_BtoB_diffenceInAmplitudes.append(r_vals[i+3]-r_vals[i+1])
            Start.append(r_time[i])
            if(r_pvs[i+4]==-1): #If ends with a valley -1,1-1,1,-1 = 2 complete Respiration Cycles
                End.append(r_time[i+3])
                #print(len(r_time),i,i+3)
                i=i+4 #Start next cycle at the valley after 2nd respiration peak
            else:
                End.append(r_time[i+3])
                #print(len(r_time),i,i+3)
                i=i+3 #Else, Start next cycle at the peak after 2nd respiration peak
        else:
            i=i+1
        
    
    newSD_B2B_Inter = [x for x in SD_B2B_Inter if math.isnan(x) == False]
    newAi_inter = [x for x in Ai_inter if math.isnan(x) == False]
    newAe_inter = [x for x in Ae_inter if math.isnan(x) == False]
    newA_inter = [x for x in A_inter if math.isnan(x) == False]
    
    newI_inter = [x for x in I_inter if math.isnan(x) == False]
    newE_inter = [x for x in E_inter if math.isnan(x) == False]
    #Feature 1 - RMSSD - The square root of the mean of the squares of the successive difference of breath-to-breath intervals
    RMSSD=np.sqrt(np.mean(np.square(newSD_B2B_Inter)))
    
    #Feature 2 - mDI - Mean of successive differences of breath-to-breath intervals
    mDI=np.mean(newSD_B2B_Inter)
               
    #Feature 3 -  MADI - Maximum absolute differences of breath-to-breath intervals
    if len(newSD_B2B_Inter)==0:
        MADI=math.nan
    else:
        MADI=max(newSD_B2B_Inter)
    
    #Feature 4 - Respiratory Rate #My: Standard deviation from Normal RR15
    SD_RR=stdev(r_pvs.count(1))
               
    #Feature 5 - RMDA - The ratio of the mean of differences between the amplitudes of expiration and inspiration
    A_Mi=np.mean(newAi_inter)
    A_Me=np.mean(newAe_inter)
    RMDA = A_Mi/A_Me
    
    ##Amplitude Feature
    A_RMSi=np.sqrt(np.mean(np.square(newAi_inter)))
    A_RMSe=np.sqrt(np.mean(np.square(newAe_inter)))
    
    RMDA_RMS = A_RMSi/A_RMSe
    
    
    #Features 6 - RMI - The ratio of the mean of expiration and inspiration intervals
    I_Mi=np.mean(newI_inter)
    I_Me=np.mean(newE_inter)
    RMI = I_Mi/I_Me 
    
    
    #Feature 7 - Amplitude Shallowless measurement
    ht_Mean_max=np.mean(ht_max)
    BPI_ht_Mean_max=r_pvs.count(1)/ht_Mean_max
    #print([minTime,maxTime,RMSSD,mDI,MADI,r_pvs.count(1),SD_RR,RMDA,RMI,A_RMSi,A_RMSe,RMDA_RMS,A_Mean_i,A_Mean_e,ht_Mean_av,ht_Mean_max,ht_RMS_av,ht_RMS_max,A_inter_mean,A_inter_RMS])
    return([minTime,maxTime,RMSSD,mDI,MADI,r_pvs.count(1),RMDA_RMS,RMI,BPI_ht_Mean_max])
    
