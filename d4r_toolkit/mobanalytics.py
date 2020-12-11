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

def home_distance(df): # df ... nighttime data for all users 
    df["distance"] = df.apply(lambda row : utils.distance(row["lat"],row["lon"],\
                                                          row["homelat"],row["homelon"]),axis=1)
    df["date_night"] = df["time_t"].apply(utils.tomidnightdate) # string of date
    df2 = df[["id","date_night","distance"]]
    df_id_date_mindist = df2.groupby(["id","date_night"])["distance"].min().reset_index()
    return df_id_date_mindist


def plotdiffforSI(date_disp, ts, si, ax,color, category, label, ylab):
    ax.plot(date_disp["date_dt"],ts, color=color, label="$\Delta D$")
    ax.fill_between(date_disp["date_dt"],ts-date_disp["error"],ts+date_disp["error"], 
                    color=color, alpha=0.3, label="95% CI")
    ax.xaxis.set_major_formatter(DateFormatter('%b %d'))
    ax.set_xticks(["20170905","20170915","20170925","20171005"])
    ax.set_ylabel(label[1])
    ax.axvline("20170919", color="red")
    ax.axhline(0, color="k")    
    ax.legend(fontsize=10, ncol=5, loc="upper left")
    ax.set_title(label+str(si))

def plotforSI(df_disp_se,si,ax,color, category, label, ylab, colname):
    df_this = df_disp_se[df_disp_se[category]==si]
    date_count = df_this.groupby('date').count().reset_index()[["date","id"]]
    date_std = df_this.groupby('date').std().reset_index()[["date",colname]]
    date_std = date_std.rename(columns= {colname:"std"})
    avg_trend = trend(df_this, 15, colname)
    date_disp = df_this.groupby('date').mean().reset_index()
    date_disp["date_dt"] = date_disp["date"].apply(lambda x : dt.strptime(str(x), '%Y%m%d'))
    date_disp["youbi"] = date_disp["date_dt"].apply(lambda x : x.weekday())
    date_disp = date_disp.merge(date_count, on="date")
    date_disp = date_disp.merge(date_std, on="date")
    avg = date_disp.merge(avg_trend, on="youbi")
    avg = avg.sort_values(by=['date'])
    #     ax.plot(date_disp["date_dt"],date_disp["samestate"], color="orange", label="out of state")
    ### plot
    ax.plot(date_disp["date_dt"],date_disp[colname], color=color, label="data")
    if ylab[0] == "D rate":
        date_disp["error"] = date_disp.apply(lambda x : 1.96*np.sqrt((x[colname]*(1-x[colname]))/x["id"]), \
                                             axis=1)
    else:
        date_disp["error"] = date_disp.apply(lambda x : 1.96*x["std"]/np.sqrt(x["id"]), axis=1)
    
    ax.fill_between(date_disp["date_dt"],date_disp[colname]-date_disp["error"], \
                    date_disp[colname]+date_disp["error"], 
                    color=color, alpha=0.3, label="95% CI")
    ax.plot(avg["date_dt"],avg["avgtrend"], color=color, linestyle= "--", label= "avg")
    ax.xaxis.set_major_formatter(DateFormatter('%b %d'))
    ax.set_xticks(["20170905","20170915","20170925","20171005"])
    # ax.set_ylim(0)
    ax.set_ylabel(ylab[0])
    ax.axvline("20170919", color="red")
    ax.legend(fontsize=10, ncol=5, loc="upper left")
    ax.set_title(label+str(si))
    
    ts = date_disp[colname].values-avg["avgtrend"].values
    plotdiffforSI(date_disp, ts, si, ax2, color, category, label, ylab)
    return date_disp["date_dt"], ts, date_disp["error"]

def plotforarea(df_jotu, area, name, si, sam, rat):
    colname = "samemun"
    date_count = df_jotu.groupby('date').count().reset_index()[["date","id"]]
    date_std = df_jotu.groupby('date').std().reset_index()[["date",colname]]
    date_std = date_std.rename(columns= {colname:"std"})
    avg_trend = trend(df_jotu, 15, colname)
    date_disp = df_jotu.groupby('date').mean().reset_index()
    date_disp["date_dt"] = date_disp["date"].apply(lambda x : dt.strptime(str(x), '%Y%m%d'))
    date_disp["youbi"] = date_disp["date_dt"].apply(lambda x : x.weekday())
    date_disp = date_disp.merge(date_count, on="date")
    date_disp = date_disp.merge(date_std, on="date")
    avg = date_disp.merge(avg_trend, on="youbi")
    avg = avg.sort_values(by=['date'])

    ### plot
    fig=plt.figure(figsize=(8,2.5))
    gs=GridSpec(1,1)

    ax = fig.add_subplot(gs[0,0]) 
    ax.plot(date_disp["date_dt"],date_disp[colname], color="b", label="data")
    date_disp["error"] = date_disp.apply(lambda x : 1.96*np.sqrt((x[colname]*(1-x[colname]))/x["id"]), axis=1)

    ax.fill_between(date_disp["date_dt"],date_disp[colname]-date_disp["error"], \
                    date_disp[colname]+date_disp["error"], 
                    color="skyblue", alpha=0.3, label="95% CI")
    ax.plot(avg["date_dt"],avg["avgtrend"], color="gray", linestyle= "--", label= "avg")
    ax.xaxis.set_major_formatter(DateFormatter('%b %d'))
    ax.set_xticks(["20170905","20170915","20170925","20171005"])
    # ax.set_ylim(0)
    ax.set_ylabel("D rate")
    ax.axvline("20170919", color="red")
    ax.legend(fontsize=10, ncol=5, loc="upper left")
    ax.set_title(name+": SI="+si+"; IDs="+sam+"("+rat+")", fontsize=14)
    
    plt.tight_layout()
    plt.savefig(outpath+"displacement_"+area+".png",
                dpi=300, bbox_inches='tight', pad_inches=0.05)
    plt.show()
    
def trend(df_this, j, colname):
    date_disp = df_this.groupby('date').mean().reset_index()[["date",colname]]
    date_disp["date_dt"] = date_disp["date"].apply(lambda x : dt.strptime(str(x), '%Y%m%d'))
    date_disp_usual = date_disp.iloc[:15]
    date_disp_usual["youbi"] = date_disp_usual["date_dt"].apply(lambda x : x.weekday())
    date_disp_usual_avg = date_disp_usual.groupby('youbi').mean().reset_index()[["youbi",colname]]
    date_disp_usual_avg_rename = date_disp_usual_avg.rename(columns={colname: "avgtrend"})
    return date_disp_usual_avg_rename

def trend_median(df_this, j, colname):
    date_disp = df_this.groupby('date').median().reset_index()[["date",colname]]
    date_disp["date_dt"] = date_disp["date"].apply(lambda x : dt.strptime(str(x), '%Y%m%d'))
    date_disp_usual = date_disp.iloc[:15]
    date_disp_usual["youbi"] = date_disp_usual["date_dt"].apply(lambda x : x.weekday())
    date_disp_usual_avg = date_disp_usual.groupby('youbi').mean().reset_index()[["youbi",colname]]
    date_disp_usual_avg_rename = date_disp_usual_avg.rename(columns={colname: "avgtrend"})
    return date_disp_usual_avg_rename