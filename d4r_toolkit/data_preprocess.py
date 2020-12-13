### import key libraries
import numpy as np
import pandas as pd
import glob, os
from datetime import datetime as dt
from datetime import timedelta
from datetime import timezone
import pytz

### import Dask library (https://dask.org/)
import dask
import dask.dataframe as dd
from dask.diagnostics import ProgressBar
from dask.distributed import Client

### load head of data files to determine column names 
def loaddata(dirpath, sep, colnames, ext):
    files = [file for file in glob.glob(dirpath+"*"+ext)]
    df = dd.read_csv(files, names=colnames, sep=sep)
    return df
            
def loaddata_takeapeek(dirpath, sep, ext):
    files = [file for file in glob.glob(dirpath+"*"+ext)]
    for i,f in enumerate(files):
        print("filename of file #"+str(i)+": "+f)
        df = dd.read_csv(f, sep=sep)
        print("head of file #"+str(i)+":")
        print(df.head())

def fromunix2fulldate(x):
    ct = pytz.timezone("America/Mexico_City")
    ### errors 
    if (int(x)<86400) or (int(x)>1609518354):
        x = 86400
    dat = dt.fromtimestamp(x, ct)
    tim = dat.strftime('%Y-%m-%d %H:%M:%S') ### date --> string
    tim2 = dat.strptime(tim, '%Y-%m-%d  %H:%M:%S') ### string --> date
    return tim2

def fromunix2date(x):
    ct = pytz.timezone("America/Mexico_City")
    ### errors 
    if (int(x)<86400) or (int(x)>1609518354):
        x = 86400
    dat = dt.fromtimestamp(x, ct)
    tim = dat.strftime('%Y-%m-%d') ### date --> string
    tim2 = dat.strptime(tim, '%Y-%m-%d') ### string --> date
    return tim2

def fromunix2time(x):
    ct = pytz.timezone("America/Mexico_City")
    if (int(x)<86400) or (int(x)>1609518354):
        x = 86400
    dat = dt.fromtimestamp(x, ct)
    tim = dat.strftime('%H:%M:%S')
    tim2 = dat.strptime(tim, '%H:%M:%S')
    return tim2

def crop_date(dff, startdt, enddt, timezone): ### input string start date 
    ct = pytz.timezone("America/Mexico_City")
    st = int(dt.strptime(startdt, "%Y/%m/%d").replace(tzinfo=ct).timestamp())
    et = int(dt.strptime(enddt, "%Y/%m/%d").replace(tzinfo=ct).timestamp())
    df_res = dff[(dff["unixtime"] <= et) & (dff["unixtime"] >= st)]
    return df_res

def crop_time(dff, nighttime_start, nighttime_end, timezone): ### input string start date 
    ct = pytz.timezone("America/Mexico_City")
    daytime1 =  dt.strptime(nighttime_start, '%H:%M:%S')
    daytime2 =  dt.strptime(nighttime_end, '%H:%M:%S')
    meta = dff['unixtime'].head(1).apply(fromunix2time)
    dff["time_t"] = dff["unixtime"].apply(lambda x: fromunix2time(x))
    dff_nighttime = dff[(dff["time_t"]<daytime1) | (dff["time_t"]>daytime2)]
    return dff_nighttime

def crop_spatial(dff, bbox):
    minlon = bbox[0]
    minlat = bbox[1]
    maxlon = bbox[2]
    maxlat = bbox[3]
    df_res = dff[(dff["lon"] <= maxlon) & (dff["lon"] >= minlon) \
                 & (dff["lat"] <= maxlat) & (dff["lat"] >= minlat)]
    return df_res

def users_totalXpoints(dff, threshold=10, plot=False):
    users_points = dff.groupby("id").count().reset_index()
    if plot==True:
        plt.figure(figsize=(8,4))
        plt.hist(users_points["gaid"].values, bins=50)
        plt.axvline(threshold, color="red")
        plt.show()
    selected_users = users_points[users_points["gaid"] > threshold]["id"]
    return selected_users

def users_Xdays(dff, threshold=10, plot=False):
#     meta = dff['unixtime'].head(1).apply(fromunix2date)
    dff["date_str"] = dff["unixtime"].apply(lambda x: fromunix2date(x))
    users_dates = dff.groupby('id')['date_str'].nunique().reset_index()
    if plot==True:
        plt.figure(figsize=(8,4))
        plt.hist(users_dates["date_str"].values, bins=50)
        plt.axvline(threshold, color="red")
        plt.show()
    selected_users = users_dates[users_dates["date_str"] > threshold]["id"]
    return selected_users

def users_Xavgps(dff, threshold=10, plot=False):
    users_points = dff.groupby("id").gaid.count()[["id","gaid"]]
#     meta = dff['unixtime'].head(1).apply(fromunix2date)
    dff["date_str"] = dff["unixtime"].apply(lambda x: fromunix2date(x))
    users_dates = dff.groupby('id')['date_str'].nunique().reset_index()[["id","date_str"]]
    if plot==True:
        plt.figure(figsize=(8,4))
        plt.hist(users_dates["date_str"].values, bins=50)
        plt.axvline(threshold, color="red")
        plt.show()
    users_data = users_points.merge(users_dates, on ="id")
    users_data["avg"] = users_data["gaid"]/users_data["date_str"]
    selected_users = users_data[users_data["avg"] > threshold]["id"]
    return selected_users

def users_Xdays_Xavgps(dff, threshold_pts, threshold_days, plot=False):
    users_points = dff.groupby("id").gaid.count().reset_index()[["id","gaid"]]
#     meta = dff['unixtime'].head(1).apply(fromunix2date)
    dff["date_str"] = dff["unixtime"].apply(lambda x: fromunix2date(x))
    users_dates = dff.groupby('id')['date_str'].nunique().reset_index()[["id","date_str"]]
    users_data = users_points.merge(users_dates, on ="id")
    users_data["avg"] = users_data["gaid"]/users_data["date_str"]
    if plot==True:
        plt.figure(figsize=(8,4))
        plt.hist(users_data["avg"].values, bins=50)
        plt.axvline(threshold_pts, color="red")
        plt.show()
    selected_users = users_data[(users_data["avg"] > threshold_pts) & \
                                (users_data["date_str"] > threshold_days)]["id"]
    dff_new = dff[dff["id"].isin(selected_users)]
    return dff_new