import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pymongo
from pymongo import MongoClient
import datetime
import time
import numpy as np
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates

client = MongoClient()

#point the client at mongo URI
client = MongoClient('mongodb://localhost:27017')
#select database
db = client['Plusword']
#select the collection within the database
test = db.Historical
#convert entire collection to Pandas dataframe
df = pd.DataFrame(list(test.find()))

#Dropping uneeded columns
df = df[['Timestamp', 'Time', 'User']]

#Formatting and setting datatypes
df["Timestamp"] = pd.to_datetime(df["Timestamp"], format ='%d/%m/%Y %H:%M')
df["Sub_Date"] = df["Timestamp"].dt.date
df["Sub_Date"] = pd.to_datetime(df["Sub_Date"], format ='%Y-%m-%d')
df["Sub_Time"] = df["Timestamp"].dt.time
df["Sub_Time"] = pd.to_datetime(df["Sub_Time"], format ='%H:%M:%S')
#df["Time_dt"] = pd.to_datetime(df["Time"], format ='%H:%M:%S')
df["User"] = df["User"].astype('category')

#Probably a better way of this doing this but couldnt get it to work
df['Year'] = pd.DatetimeIndex(df['Sub_Date']).year
df['Month'] = pd.DatetimeIndex(df['Sub_Date']).month
df.dtypes

#Splits time into three seperate columns
df[["Time_h", "Time_m", "Time_s"]] = df["Time"].str.split(':', expand=True)

#Makes them all ints
df[["Time_h", "Time_m", "Time_s"]] = df[["Time_h", "Time_m", "Time_s"]].astype(int)

#Converts hours and minutes to seconds and then adds them to make total time in seconds
df["Time_in_seconds"] = (df["Time_h"] * 3600) + (df["Time_m"] * 60) +(df["Time_s"])
df=df[["Timestamp", "Time", "User", "Sub_Date", "Sub_Time", "Year", "Month", "Time_in_seconds"]]


df["timedelta"] = pd.to_timedelta(df["Time"])
df["Time"] = pd.to_datetime(df["Time"], format ='%H:%M:%S')

#Avg, min, max, number of submissions and sub minnies for overall high/low scores

df_overall_max_time = df.groupby(df["User"])["timedelta"].max()
#df_overall_max_time = df.groupby(df["User"])["Time_in_seconds"].max()
df_overall_max_time= df_overall_max_time.reset_index()

df_overall_min_time = df.groupby(df["User"])["Time_in_seconds"].min()
df_overall_min_time= df_overall_min_time.reset_index()

df_overall_mean_time = df.groupby(df["User"])["Time_in_seconds"].mean()
df_overall_mean_time= df_overall_mean_time.reset_index()

df_overall_number_submissions = df.groupby(df["User"])["User"].count() #Done

# Number of subminnies -Done

df_sub_minnies = df.set_index('Time').between_time('00:00:00', '00:01:00')
df_sub_minnies= df_sub_minnies.groupby(df_sub_minnies["User"])["User"].count()
df_sub_minnies = df_sub_minnies[df_sub_minnies!=0]

#Avg, min, max times for submission time for seeing who is the earliest of birds

df_latest_sub = df.groupby(df["User"])["Sub_Time"].max()
df_earliest_sub = df.groupby(df["User"])["Sub_Time"].min()
df_mean_sub = df.groupby(df["User"])["Sub_Time"].mean()

#Avg, min, max times for each person over by month and year for trending

df_monthly_mean_time = df.groupby(["User", "Year", "Month"])["Time"].mean()
df_monthly_mean_time = df_monthly_mean_time.dropna()

df_monthly_max_time = df.groupby(["User", "Year", "Month"])["Time"].max()
df_monthly_max_time = df_monthly_max_time.dropna()

df_monthly_min_time = df.groupby(["User", "Year", "Month"])["Time"].min()
df_monthly_min_time = df_monthly_mean_time.dropna()


## Plotting

# specify a date to use for the times
zero = datetime.datetime(2022,6,20)
time = [zero + t for t in df_overall_max_time.timedelta]

# convert datetimes to numbers
zero = mdates.date2num(zero)
time = [t-zero for t in mdates.date2num(time)]

f = plt.figure()
ax = f.add_subplot(1,1,1)

f=sns.barplot(x=df_overall_max_time.User, y=time).set(
            title='Longest Submitted Time',
            ylabel='Time')
ax.yaxis_date()
ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
plt.show()

#Number of sub minnies

sns.barplot(kind='bar', title='Number of sub-1 minute times')
plt.xticks(rotation=0)

plt.show()

#Number of submissions

df_overall_number_submissions.plot(kind='bar', title='Number of Submissions')
plt.xticks(rotation=0)

plt.show()
