from math import sin, cos, sqrt, atan2, radians
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob, os
from datetime import datetime as dt
from datetime import timedelta
from datetime import timezone
import pytz
from d4r_toolkit import utils

def stars(p_val):
    stars = ""
    if p_val<0.01:
        stars = "***"
    elif p_val < 0.05:
        stars = "**"
    elif p_val < 0.1:
        stars = "*"
    return stars

# returns distance in km
def distance(lat1,lon1,lat2,lon2):
    R = 6373.0
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

def insidebox(lat,lon,maxlat,minlat,maxlon,minlon):
    if (lat<maxlat) & (lat>minlat) & (lon>minlon) & (lon<maxlon):
        return True
    else:
        return False

def fromunix2yyyymmddhh(x):
    ct = pytz.timezone("America/Mexico_City")
    ### errors 
    if (int(x)<86400) or (int(x)>1609518354):
        x = 86400
    dat = dt.fromtimestamp(int(x), ct)
    tim = dat.strftime('%Y-%m-%d %H') ### date --> string
    return tim

def count_filenum(root):
    c=0
    for file in os.listdir(root):
        if file.endswith(".gz"):
            c+=1
    return c

def tomidnightdate(datetime):
    datetimestr = datetime.strftime('%Y-%m-%d %H:%M:%S')
    hour = int(datetimestr.split(" ")[1].split(":")[0])
    if hour>12:
        thisdate = datetimestr.split(" ")[0]
    else:
        date_d = dt.strptime(datetimestr.split(" ")[0], "%Y-%m-%d")
        thisdate = (date_d - timedelta(days=1)).strftime('%Y-%m-%d')
    return thisdate