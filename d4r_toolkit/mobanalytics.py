### import key libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob, os
from datetime import datetime as dt
from datetime import timedelta
from datetime import timezone
import pytz
from d4r_toolkit import utils

from sklearn import cluster

def meanshift(df, bw=0.01):
    if len(df)>100:
        df = df.sample(frac=0.01)
    ms = cluster.MeanShift(bandwidth=bw)
    ms.fit(df[["lon","lat"]])
    labels = ms.labels_
    counts = np.bincount(labels)
    most = np.argmax(counts)
    cluster_centers = ms.cluster_centers_
    return cluster_centers[most]

def meanshift_raw(arr, bw=0.01):
    ms = cluster.MeanShift(bandwidth=bw)
    ms.fit(arr)
    labels = ms.labels_
    counts = np.bincount(labels)
    most = np.argmax(counts)
    cluster_centers = ms.cluster_centers_
    return cluster_centers[most]

def density_nomap(latitudes, longitudes, center, bins, radius):
    
    # Center the map around the provided center coordinates
    histogram_range = [
        [center[1] - radius, center[1] + radius],
        [center[0] - radius, center[0] + radius]
    ]
    
    res = plt.hist2d(longitudes, latitudes, bins=bins, norm=LogNorm(),
               range=histogram_range)

    return res

def density_map(latitudes, longitudes, center, bins, radius, ax):
    
    cmap = copy.copy(plt.cm.jet)
    cmap.set_bad((0,0,0))  # Fill background with black

    # Center the map around the provided center coordinates
    histogram_range = [
        [center[1] - radius, center[1] + radius],
        [center[0] - radius, center[0] + radius]
    ]
    
    res = ax.hist2d(longitudes, latitudes, bins=bins, norm=LogNorm(),
               cmap=cmap, range=histogram_range)

    ax.annotate("CDMX",   xy=(-98.85,19.5), xycoords='data', color="white", fontsize=14)
    ax.annotate("Puebla", xy=(-98.5,18.8), xycoords='data', color="white", fontsize=14)
    ax.annotate("Toluca", xy=(-99.75,19.5), xycoords='data', color="white", fontsize=14)
    ax.annotate("Cuernavaca", xy=(-99.4,18.65), xycoords='data', color="white", fontsize=14)
    ax.axis('equal')
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.grid('off')
    ax.axis('off')
    
    return res

def shori_density_map(diff, xbins, ybins, center, radius, ax, anno, vmin, vmax):  

    divnorm = mcolors.SymLogNorm(linthresh=1.0, linscale=1.0, vmin=vmin, vmax=vmax)
    cmap = copy.copy(plt.cm.jet)
    diff = np.ma.masked_where(diff == 0, diff)
    cmap.set_bad(color='black')  # Fill background with black
    
    res = ax.imshow(diff, cmap=cmap, 
                    extent=[xbins[0],xbins[-1],ybins[0],ybins[-1]], 
                    norm=divnorm,
                    origin="lower")
    divider = mpl_toolkits.axes_grid1.make_axes_locatable(ax)
    cax = divider.append_axes('right', '5%', pad='3%')
    fig.colorbar(res, cax=cax)
    
    if anno==True:
        ax.annotate("CDMX",   xy=(-98.85,19.5), xycoords='data', color="white", fontsize=14)
        ax.annotate("Puebla", xy=(-98.5,18.8), xycoords='data', color="white", fontsize=14)
        ax.annotate("Toluca", xy=(-99.75,19.5), xycoords='data', color="white", fontsize=14)
        ax.annotate("Cuernavaca", xy=(-99.4,18.65), xycoords='data', color="white", fontsize=14)
    ax.axis('equal')
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.grid('off')
    ax.axis('off')
    
    return res

def shori_density_map_norm(diff, xbins, ybins, center, radius, ax, anno,title, vmin, vmax):  

    divnorm = DivergingNorm(vmin=-3, vcenter=0, vmax=3)
    cmap = copy.copy(plt.cm.jet)
    diff = np.ma.masked_where(diff == 0, diff)
    cmap.set_bad(color='black')  # Fill background with black
    
    res = ax.imshow(diff, cmap=cmap, 
                    extent=[xbins[0],xbins[-1],ybins[0],ybins[-1]], 
                    norm=divnorm,
                    origin="lower")
    divider = mpl_toolkits.axes_grid1.make_axes_locatable(ax)
    cax = divider.append_axes('right', '5%', pad='3%')
    cbar = fig.colorbar(res, cax=cax)
    cbar.set_label("Z score", fontsize=14)
    
    if anno==True:
        ax.annotate("CDMX",   xy=(-98.85,19.5), xycoords='data', color="white", fontsize=14)
        ax.annotate("Puebla", xy=(-98.5,18.8), xycoords='data', color="white", fontsize=14)
        ax.annotate("Toluca", xy=(-99.75,19.5), xycoords='data', color="white", fontsize=14)
        ax.annotate("Cuernavaca", xy=(-99.4,18.65), xycoords='data', color="white", fontsize=14)
    ax.axis('equal')
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.grid('off')
    ax.axis('off')
    
    ax.set_title(title, fontsize=14, pad=10)
    
    return res

def getdensity_mean_std(home, normals, center, bins, rad):
    maps_d = []
    for normal in normals:
        df = pd.read_csv(staypointfile, header=None, 
                         names=["id","date","label","dlon","dlat","nlon","nlat"])
        df3 = df[(df["date"]=="20170919") & (df["label"]=="daytime")]
        df2 = df3[df3["dlon"]!=0]
        heatmap = density_nomap(df2["dlat"],df2["dlon"], center, bins, rad)
        maps_d = heatmap[0].T if maps_d == [] else maps_d + heatmap[0].T
    avgmaps_d = maps_d/len(normals)    

    maps_n = []
    for normal in normals:
        df = pd.read_csv(staypointfile, header=None, 
                         names=["id","date","label","dlon","dlat","nlon","nlat"])
        df3 = df[(df["date"]=="20170919") & (df["label"]=="daytime")]
        df2 = df3[df3["dlon"]!=0]
        heatmap = density_nomap(df2["dlat"],df2["dlon"], center, bins, rad)
        maps_n = heatmap[0].T if maps_n == [] else maps_n + heatmap[0].T
    avgmaps_n = maps_n/len(normals)    

    stdmaps_d = []
    for normal in normals:
        df = pd.read_csv(staypointfile, header=None, 
                         names=["id","date","label","dlon","dlat","nlon","nlat"])
        df3 = df[(df["date"]=="20170919") & (df["label"]=="daytime")]
        df2 = df3[df3["dlon"]!=0]
        heatmap = density_nomap(df2["dlat"],df2["dlon"],center, bins, rad)
        stdmaps_d = (heatmap[0].T - avgmaps_d)**2 if stdmaps_d == [] else stdmaps_d + \
        (heatmap[0].T - avgmaps_d)**2
    stdmaps_d = np.sqrt(stdmaps_d/10)

    stdmaps_n = []
    for normal in normals:
        df = pd.read_csv(staypointfile, header=None, 
                         names=["id","date","label","dlon","dlat","nlon","nlat"])
        df3 = df[(df["date"]=="20170919") & (df["label"]=="daytime")]
        df2 = df3[df3["dlon"]!=0]
        heatmap = density_nomap(df2["dlat"],df2["dlon"], center, bins, rad)
        stdmaps_n = (heatmap[0].T - avgmaps_n)**2 if stdmaps_n == [] else stdmaps_n + \
        (heatmap[0].T - avgmaps_n)**2
    stdmaps_n = np.sqrt(stdmaps_n/10)
    
    return [avgmaps_d,avgmaps_n,stdmaps_d,stdmaps_n]


def getdensitydata(metricsf, alldataf, chunk):
    with open(metricsf, 'w') as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')    
        done_IDs = set()
        count = 100 ### just for initial value
        while count > 0:
            id_dt_ll = data_intomap(alldataf, done_IDs, chunk)
            calc_staypoint(id_dt_ll, df_idhome, writer)
            for thisid in id_dt_ll.keys():
                done_IDs.add(thisid)
            count = len(id_dt_ll)
            print("done",len(done_IDs),count,dt.now(),dt.now()-start)

### id - date - day/night - points
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
                label = "daytime"
                if (hour<9) or (hour>21):
                    label = "nighttime"
                if hour<=4:
                    d = dt.timedelta(days=1)
                    date_dt = date_dt - d
                date_str = date_dt.strftime('%Y-%m-%d')
                lat = toks[2]
                lon = toks[3]
                if thisid in id_dt_ll.keys():
                    if date_str in id_dt_ll[thisid].keys():
                        if label in id_dt_ll[thisid][date_str].keys():
                            arr = id_dt_ll[thisid][date_str][label]
                            newarr = np.vstack((arr,[lat,lon]))
                            id_dt_ll[thisid][date_str][label] = newarr
                        else:
                            arr = [lat,lon]
                            id_dt_ll[thisid][date_str][label] = arr
                    else:
                        arr = [lat,lon]
                        tmp = {}
                        tmp[label] = arr
                        id_dt_ll[thisid][date_str] = tmp
                else:
                    if len(id_dt_ll)<chunk:
                        arr = [lat,lon]
                        tmp = {}
                        tmp[label] = arr
                        tmp2 = {}
                        tmp2[date_str] = tmp
                        id_dt_ll[thisid] = tmp2
            if i>0 and i%1000==0:
                print("done",i,dt.now(),dt.now()-start)
                start = dt.now()
                break
    return id_dt_ll


def calc_staypoint(id_dt_ll, idhome, writer):
    for thisid in id_dt_ll.keys():
        home = idhome[idhome["id"]==thisid][["homelat","homelon"]].values[0]
        for date_str in id_dt_ll[thisid].keys():
            dayp = (0,0)
            nightp = (0,0)
            if "daytime" in id_dt_ll[thisid][date_str].keys():
                arr = id_dt_ll[thisid][date_str]["daytime"]
                dayp = mobanalytics.meanshift_raw(arr)
            if "nighttime" in id_dt_ll[thisid][date_str].keys():
                arr = id_dt_ll[thisid][date_str]["nighttime"]
                nightp = mobanalytics.meanshift_raw(arr)
            writer.writerow([thisid,date_str,label,dayp[0],dayp[1],nightp[0],nightp[1]])










