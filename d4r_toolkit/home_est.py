### import key libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob, os
from datetime import datetime as dt
from datetime import timedelta
from datetime import timezone
import pytz

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