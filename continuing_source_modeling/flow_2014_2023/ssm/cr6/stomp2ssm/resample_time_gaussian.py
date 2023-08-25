"""
resample_time.py


takes STOMP timeseries and resamples it to MODFLOW timesteps

"""
import os
import numpy as np
from scipy.signal import gaussian
from scipy.ndimage import filters

 
def read_stomp_ts(fname, target_col=5):
    """ yeids the stomp data"""
    with open(fname, "r") as f:
        for ix, line in enumerate(f.readlines()):
            if ix ==0:
                continue
            vals = list(map(float, line.split(",")))
            time = vals[1]
            yield time, vals[target_col]

def read_modflow_ts(fname, tmult=1):
    """ yields the modflow time steps
    
    file is assumed to be of form
    sp start end ....

    start/end columns are multiplied by tmult
    
    """
    with open(fname, "r") as f:
        for ix, line in enumerate(f.readlines()):
            if ix==0:
                continue
            vals = line.split(",")
            sp = int(vals[0])
            vals = list(map(float, vals[1:]))
            start = vals[0]
            end = vals[1]
            yield sp, start*tmult, end*tmult

def resample(outeriter, inneriter):
    """

    take two iterables; the outer has a course timestep, the inner has a fine
    timestep (this assumes they are ordered)

    while the inner is within the bounds of the outer,
       - 1) sum
       - 2) divide by the length of the outer

    the result is the average value over the outer's time interval
    """
    for sp, start, end in outeriter:
        keepgoing = True
        outer_result = 0
        last_time = -1
        inner_result = 0
        N = 0
        inner_time = 0
        while keepgoing:
            time, val = next(inneriter)
            if abs(time - last_time)<1e-6 or (inner_result==0):
                N+=1
                inner_result+=val
            else:
                #outer_result+= (inner_result/N)*(time-inner_time)
                outer_result = inner_result
                inner_time = time
                N = 0
                inner_result = 0
            last_time=time
            if time >= end:
                keepgoing = False
        yield sp, start, end, (end-start), outer_result, outer_result/(end - start)


def resample_sum(outeriter, inneriter):
    last_val = 0
    val = 0
    prev_stomp_val = 0
    for sp, start, end in outeriter:
        keepgoing = True
        while keepgoing:
            time, val = next(inneriter)

            if time>end:
                yield sp, start, end, (end-start), prev_stomp_val-last_val, (prev_stomp_val-last_val)/((end-start)*365.25)
                last_val = val
                last_stop = end
                last_start = start
                keepgoing = False
            prev_stomp_val = val

def resample_sum_movingavg(outeriter, inneriter):
    val = 0
    accum_stomp_val=0
    for sp, start, end in outeriter:
        keepgoing = True
        while keepgoing:
            time, val = next(inneriter)
            if time>=start:            
                if time>end:
                    yield sp, start, end, (end-start), (accum_stomp_val+val), (accum_stomp_val+val)/((end-start)*365.25)
                # needed to add the val to accum_stomp_val because the End of Stress Period is not equal to Start of next, and one
                # value was not being utilized. See Kevin_Original_resampled.xlsx in 120-KE-6 folder
                    keepgoing = False
                    accum_stomp_val=0
                    val=0
                else:
                    accum_stomp_val +=val
                

            
            
def resample_7p_ave(an_iterator):
    """
    this function assumes that an_iterator has a structure like [[time, value], [time, value], [time, value], ..etc]
    """
    current_count = 0
    current_value = 0 
    for time, value in an_iterator:
         current_value += value
         current_count += 1
         if current_count > 6:
             yield time, current_value/current_count
             current_count = 0
             current_value = 0           
        
    
def running_mean(an_iterator):
    
    l = []
    t = []
    print ('creating list\n')
    for time, value in an_iterator:
#        print value
        l.append(value)
        t.append(time)

    l=list(np.diff(l))
    l.append(l[-1])

    b = gaussian(5, 1)
	#ga = filtfilt(b/b.sum(), [1.0], y)
    ga = filters.convolve1d(np.asarray(l), b/b.sum())
    list_ga=list(ga)    
    for i in range( 0, len(l)):    
        yield t[i],list_ga[i]
    
        
        
        
        
        
    
                
            
            
def process(mpath, tpath, outfile, tmult):

    outerit = read_modflow_ts(mpath, tmult)
    print ('outerit\n')
    innerit = running_mean(read_stomp_ts(tpath))
    print ('innerit\n')
    
    #innerit2 = running_mean(read_stomp_ts(tpath))
    header = ",".join(["sp","start","end","dt","sum for sp","sum/dt"])
#    data = list(resample_sum(outerit, innerit))
    data = list(resample_sum_movingavg(outerit, innerit))    
        
    
    
    #data2 = list(resample_sum(outerit, innerit2))
    with open(outfile, "w") as f:
        f.write(header+"\n")
        for line in data:
            f.write(",".join(map(str, line))+"\n")
    return data

if __name__ == "__main__":
    basepath = os.path.join(
            "unversioned","100k_release_model_forKevin")
    mpath = os.path.join(basepath, "stress_periods.csv")
    tpath = os.path.join(basepath, "120-KW-5","release_timeseries.csv")
    outfile = os.path.join(basepath, "120-KW-5","resampled.csv")
    tmult = 1
    process(mpath, tpath, outfile, tmult)
