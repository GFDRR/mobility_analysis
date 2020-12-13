import os
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

def get_poicount(gpsroot, file, maxlat, minlat, maxlon, minlon, shelterloc, df_idhome, outputpath):
    poi_datetime_ids = {}
    start = dt.now()
    filepath = os.path.join(gpsroot, file)
    print(filenum," out of ",file_num," : ",filepath)
    filenum+=1
    with gzip.open(filepath,'rt') as f:
        for i,line in enumerate(f):
            toks = line.split(",")
            lon = float(toks[4]);
            lat = float(toks[3]);
            if insidebox(lat,lon,maxlat,minlat,maxlon,minlon):
                thisid = toks[0]
                if thisid in allids:
                    tmpdist,ind = tree.query(np.asarray((lat,lon)).reshape(1,2), k=1)
                    if tmpdist<0.01:
                        poi = ind[0][0]
                        poilat,poilon = Ps[poi]
                        dist = utils.distance(lat,lon,poilat,poilon)
                        radius = shelterloc.loc[poi][["radius"]].values[0]/1000 ## kilometers
                        if dist<radius:
                            home = df_idhome[df_idhome["id"]==thisid][["homelat","homelon"]].values[0]
                            home_dist = utils.distance(lat,lon,home[0],home[1])
                            if home_dist > 0.2:
                                unixtime = toks[6]
                                date = utils.fromunix2yyyymmddhh(unixtime)
                                if poi in poi_datetime_ids.keys():
                                    if date in poi_datetime_ids[poi].keys():
                                        poi_datetime_ids[poi][date].add(thisid)
                                    else:
                                        tmpset = set()
                                        tmpset.add(thisid)
                                        poi_datetime_ids[poi][date] = tmpset
                                else:
                                    tmpset = set()
                                    tmpset.add(thisid)
                                    tmpdict = {}
                                    tmpdict[date] = tmpset
                                    poi_datetime_ids[poi] = tmpdict
            if i>0 and i%100000==0:
                print("done",i,dt.now(),dt.now()-start)
                start = dt.now()
    with open(outputpath+'pickle_'+file.split(".gz")[0]+'.pickle', 'wb') as handle:
        pickle.dump(poi_datetime_ids, handle, protocol=pickle.HIGHEST_PROTOCOL)   
        
def collectresults_intodf(gpsroot,outputpath):
    poi_datetime_ids = {}
    for file in os.listdir(gpsroot):
        if file.endswith(".gz"):
            with open(outputpath+'pickle_'+file.split(".gz")[0]+'.pickle', 'rb') as handle:
                data = pickle.load(handle)
                for poi in data.keys():
                    for date in data[poi].keys():
                        for thisid in data[poi][date]:
                            if p in poi_datetime_ids.keys():
                                if date in poi_datetime_ids[poi].keys():
                                    poi_datetime_ids[poi][date].add(thisid)
                                else:
                                    tmpset = set()
                                    tmpset.add(thisid)
                                    poi_datetime_ids[poi][date] = tmpset
                            else:
                                tmpset = set()
                                tmpset.add(thisid)
                                tmpdict = {}
                                tmpdict[date] = tmpset
                                poi_datetime_ids[poi] = tmpdict
    
    df = pd.DataFrame()
    for poi in poi_datetime_ids.keys():
        for date in poi_datetime_ids[poi].keys():
            ids = poi_datetime_ids[poi][date]
            size = len(ids)
            ids_list = list(ids)
            df = df.append({"poi_index":poi, "date":date, "num":size, "ids":ids_list}, 
                           ignore_index=True)
    df = df.astype({'poi_index': 'int32', 'num': 'int32'})
    return df