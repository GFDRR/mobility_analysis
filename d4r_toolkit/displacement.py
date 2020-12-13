from scipy.optimize import minimize
import numpy as np
import os
import csv
import gzip
import numpy as np
import pandas as pd
from sklearn.neighbors import KDTree
from math import sin, cos, sqrt, atan2, radians
from datetime import datetime as dt
from datetime import timedelta
from datetime import timezone
import pytz
import pickle

def fit_baseline(data,baseline):
    
    def axb(p,x):    
        return p[0]*x
    
    def errortot(data, baseline):
        tot = 0
        for i in np.arange(15):
            tot = tot + (baseline[i]-data[i])**2
        return tot
    
    x0 = np.array([1])
    res = minimize(lambda p: errortot(axb(p, data), baseline), x0=x0, method='Powell')

    return res.x


def getdataforIDs(alldataf, gpsroot, allids):
    with open(alldataf, 'w') as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')
        filenum=1
        file_num = count_filenum(gpsroot)
        for file in os.listdir(gpsroot):
            if file.endswith(".gz"):
                print("----",dt.now())
                poi_datetime_ids = {}
                start = dt.now()
                filepath = os.path.join(gpsroot, file)
                print(filenum," out of ",file_num," : ",filepath)
                filenum+=1
                with gzip.open(filepath,'rt') as f:
                    for i,line in enumerate(f):
                        toks = line.split(",")
                        lon = toks[4]
                        lat = toks[3]
                        thisid = toks[0]
                        if thisid in allids:
                            unixtime = toks[6]
                            date = utils.fromunix2yyyymmddhhmmss(unixtime)
                            writer.writerow([thisid,date,lat,lon])
                        if i>0 and i%1000==0:
                            print("done",i,dt.now(),dt.now()-start)
                            start = dt.now()
                            break
                if filenum==1:
                    break

def getdisplacementdata(metricsf, alldataf, chunk):
    with open(metricsf, 'w') as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')    
        done_IDs = set()
        count = 100 ### just for initial value
        while count > 0:
            id_dt_ll = data_intomap(alldataf, done_IDs, chunk)
            calc_displacement(id_dt_ll, df_idhome, writer)
            for thisid in id_dt_ll.keys():
                done_IDs.add(thisid)
            count = len(id_dt_ll)
            print("done",len(done_IDs),count,dt.now(),dt.now()-start)

def data_intomap(alldataf, done_IDs, chunk):
    id_dt_ll = {}
    start = dt.now()
    with gzip.open(alldataf,'rt') as f:
        for i,line in enumerate(f):
            toks = line.split(",")
            thisid = toks[0]
            if thisid not in done_IDs:
                datetime = toks[1]
                date_dt = dt.strptime(datetime.split(" ")[0], "%Y-%m-%d")
                hour = int(datetime.split(" ")[1].split(":")[0])
                if (hour<9) or (hour>21):
                    if hour<=4:
                        d = dt.timedelta(days=1)
                        date_dt = date_dt - d
                    date_str = date_dt.strftime('%Y-%m-%d')
                    lat = toks[2]
                    lon = toks[3]
                    if thisid in id_dt_ll.keys():
                        if date_str in id_dt_ll[thisid].keys():
                            arr = id_dt_ll[thisid][date_str]
                            newarr = np.vstack((arr,[lat,lon]))
                            id_dt_ll[thisid][date_str] = newarr
                        else:
                            arr = [lat,lon]
                            id_dt_ll[thisid][date_str] = arr
                    else:
                        if len(id_dt_ll)<chunk:
                            arr = [lat,lon]
                            tmp = {}
                            tmp[date_str] = arr
                            id_dt_ll[thisid] = tmp
            if i>0 and i%1000==0:
                print("done",i,dt.now(),dt.now()-start)
                start = dt.now()
                break
    return id_dt_ll

def calc_displacement(id_dt_ll, idhome, writer):
    for thisid in id_dt_ll.keys():
        home = idhome[idhome["id"]==thisid][["homelat","homelon"]].values[0]
        for date_str in id_dt_ll[thisid].keys():
            arr = id_dt_ll[thisid][date_str]
            tmptotal = 0
            mindist  = 100000
            minll = (0,0)
            for ar in arr:
                dist = utils.distance(home[0],home[1],ar[0],ar[1])
                if dist<mindist:
                    mindist = dist
                    minll = (ar[0],ar[1])
                tmptotal = tmptotal + dist
            avgdist = tmptotal/len(arr)
            writer.writerow([thisid,date_str,home[0],home[1],mindist,avgdist,minll[0],minll[1]])
            