import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient
import datetime
import matplotlib.dates as mdates
import numpy as np
from scipy import interpolate, signal
import base64
import streamlit as st


def settings():
    # Sets plot style

    sns.set_theme()

    # Sets colour for each person
    palette = {"Sal": "tab:cyan",
               "Joe": "tab:orange",
               "Oli": "tab:purple",
               "Tom": 'tab:pink',
               "George": 'tab:olive',
               "Harvey": "tab:red"}


    # Default value for rolling average window duration
    window_days = 60

    return palette, window_days


def time_delta_to_num(time_delta):
    """ Takes in time delta and converts it into a number for plotting"""

    # specify a date to use for the times

    zero_date = datetime.datetime(2022, 6, 20)

    zero_num = mdates.date2num(zero_date)

    # adds zero_data to timedelta to convert

    time_delta_plus_date = [zero_date + time_unit for time_unit in time_delta]

    # convert datetimes to numbers

    time_delta_as_num = [mins - zero_num for mins in mdates.date2num(time_delta_plus_date)]

    return time_delta_as_num


def time_delta_as_num_to_time(df):
    """Creates a human-readable time from a timedelta and strips the UNIX date from the value to just leave the time"""

    df['Time'] = mdates.num2date(df['time_delta_as_num'])

    df['Time'] = df['Time'].dt.time

    df['Time'] = df['Time'].astype('string')

    df['Time'] = df['Time'].str[:8]

    return df


def y_axis_generator(max_y_value, unit):
    """Creates range for y axis from 0 to max_y_value then passes it to time_delta_to_num. Returns y axis values as
    plottable number"""

    y_axis_time_range = list(range(0, max_y_value, 1))

    y_axis_time_delta = pd.to_timedelta(y_axis_time_range, unit=unit)

    y_axis_time_num = time_delta_to_num(y_axis_time_delta)

    return y_axis_time_num


def spline_smooth(df):
    """Smooths lines via interpolation and splines. Purely cosmetic"""

    df_spline = df.copy()

    df_spline['date_as_num'] = mdates.date2num(df_spline['timestamp'])

    x_smooth = np.linspace(df_spline['date_as_num'].min(), df_spline['date_as_num'].max(), 25)

    bspline = interpolate.make_interp_spline(df_spline['date_as_num'], df_spline['time_delta_as_num'])

    y_smooth = bspline(x_smooth)

    return x_smooth, y_smooth


def savgol_smooth(df):
    """Smooths lines using a Savitzky–Golay filter"""

    df_savgol = df.copy()

    df_savgol['date_as_num'] = mdates.date2num(df_savgol['timestamp'])

    max_window = len(df_savgol)

    polynomial_order = 10

    x_smooth = signal.savgol_filter(df_savgol['date_as_num'], max_window, polynomial_order)

    y_smooth = signal.savgol_filter(df_savgol['time_delta_as_num'], max_window, polynomial_order)

    return x_smooth, y_smooth


def data_import():
    """Connects to database and creates dataframe containing all columns. Drops unneeded columns and sets timestamp
     datatype. Creates submission time from timestamp and converts both submission time and completion time to time
     deltas represented as plottable numbers. Finally, drops submission time column as no longer needed"""

    # Database details
    mongodb_host = 'localhost'

    mongodb_port = 27017

    # point the client at mongo URI

    client = MongoClient(mongodb_host, mongodb_port)

    # Connects to database and loads data

    db = client.plusword

    collection = db.historical_data

    df = pd.DataFrame(list(collection.find()))

    # Dropping columns and setting datatypes

    df = df[['timestamp', 'time', 'user']]

    df["timestamp"] = pd.to_datetime(df["timestamp"], format='%d/%m/%Y %H:%M')

    # Converting time and submission time to timedelta

    df["time_delta"] = pd.to_timedelta(df["time"])

    df['sub_time_delta'] = df['timestamp'].dt.strftime('%H:%M:%S').astype('timedelta64')

    # Converting timedeltas to plottable numbers and dropping sub_time_delta

    for col in ['time_delta', 'sub_time_delta']:
        df['new'] = df[col].astype('timedelta64[ns]')

        df['new'] = time_delta_to_num(df['new'])

        df.rename(columns={'new': str(col) + '_as_num'}, inplace=True)

    df = df.drop(columns="sub_time_delta")

    df = df.rename(columns={'user': 'User'})

    return df


def overall_max_time(df, palette):
    """Barplot showing the longest completion time for each person """

    df_overall_max_time = df.groupby(df["User"])["time_delta_as_num"].max()

    df_overall_max_time = df_overall_max_time.reset_index()

    df_overall_max_time = df_overall_max_time.sort_values(by='time_delta_as_num', ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))

    fig = sns.barplot(data=df_overall_max_time,
                      x="User",
                      y="time_delta_as_num",
                      palette=palette).set(
        ylabel='Time /mins',
        xlabel=None)

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    df_overall_max_time = time_delta_as_num_to_time(df_overall_max_time)

    df_overall_max_time = df_overall_max_time[['User', 'Time']]

    return df_overall_max_time, ax.figure


def overall_min_time(df, palette):
    """Barplot showing the shortest completion time for each person """

    df_overall_min_time = df.groupby(df["User"])["time_delta_as_num"].min()

    df_overall_min_time = df_overall_min_time.reset_index()

    df_overall_min_time = df_overall_min_time.sort_values(by='time_delta_as_num', ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))

    fig = sns.barplot(data=df_overall_min_time,
                      x="User",
                      y="time_delta_as_num",
                      palette=palette).set(
        ylabel='Time /mins',
        xlabel=None)

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    df_overall_min_time = time_delta_as_num_to_time(df_overall_min_time)

    df_overall_min_time = df_overall_min_time[['User', 'Time']]

    return df_overall_min_time, ax.figure


def overall_mean_time(df, palette):
    """Barplot showing mean completion time for each person """

    # Creates df

    df_overall_mean_time = df.groupby(df["User"])["time_delta_as_num"].mean()

    df_overall_mean_time = df_overall_mean_time.reset_index()

    df_overall_mean_time = df_overall_mean_time.sort_values(by='time_delta_as_num', ascending=False)

    # Plot

    fig, ax = plt.subplots(figsize=(10, 5))

    fig = sns.barplot(data=df_overall_mean_time,
                      x="User",
                      y="time_delta_as_num",
                      palette=palette).set(
        ylabel='Time /mins',
        xlabel=None)

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    # Formats df for display

    df_overall_mean_time = time_delta_as_num_to_time(df_overall_mean_time)

    df_overall_mean_time = df_overall_mean_time[['User', 'Time']]

    return df_overall_mean_time, ax.figure


def number_of_sub_1_minnies(df, palette):
    """ Barplot of how many sub 1-minute completion times for each person"""

    # Creates df

    df_sub_minnies = df[df["time_delta"] < datetime.timedelta(minutes=1)]

    df_sub_minnies = df_sub_minnies.groupby(df_sub_minnies["User"])["timestamp"].count()

    df_sub_minnies = df_sub_minnies.reset_index()

    df_sub_minnies = df_sub_minnies.rename(columns={'timestamp': 'Number of Sub 1 Minutes'})

    # Plot

    fig, ax = plt.subplots(figsize=(10, 5))

    fig = sns.barplot(data=df_sub_minnies,
                      y='Number of Sub 1 Minutes',
                      x='User',
                      palette=palette).set(
        ylabel=None,
        xlabel=None)

    plt.xticks(rotation=0)

    return df_sub_minnies, ax.figure


def number_of_submissions(df, palette):
    """ Barplot of how many submissions total for each person"""

    # Creates df

    df_overall_number_submissions = df["User"].value_counts(sort=True, ascending=False)

    df_overall_number_submissions = df_overall_number_submissions.reset_index()

    df_overall_number_submissions = df_overall_number_submissions.rename(columns={'User': 'Number of Submissions',
                                                                                  'index': 'User'})
    # Plot

    fig, ax = plt.subplots(figsize=(10, 5))

    fig = sns.barplot(data=df_overall_number_submissions,
                      y='Number of Submissions',
                      x='User',
                      palette=palette)

    plt.xticks(rotation=0)

    return df_overall_number_submissions, ax.figure


def combined_monthly_mean_lineplot(df, palette):
    """Plots monthly mean times for every player over time on the same lineplot"""

    # Creates df

    df_monthly_mean_time = df.groupby(["User", df["timestamp"].dt.to_period('M')])["time_delta_as_num"].mean()

    df_monthly_mean_time = df_monthly_mean_time.reset_index()

    df_monthly_mean_time["timestamp"] = df_monthly_mean_time["timestamp"].astype('datetime64[M]')

    # Generates 15 minutes for y axis

    y_axis_time = y_axis_generator(15, 'm')

    # Selects every 2 minutes

    y_axis_time_2_mins = y_axis_time[::2]

    # Plot

    fig, ax = plt.subplots(figsize=(15, 7))

    # Smooths lines out for each user and plots them

    df_smooth = pd.DataFrame()

    for user in df_monthly_mean_time['User'].unique():
        df_monthly_mean_time_rough = df_monthly_mean_time[df_monthly_mean_time['User'] == user]

        x_smooth, y_smooth = spline_smooth(df_monthly_mean_time_rough)

        # converts x_smooth, y_smooth into a dataframe with user value associated with them

        user_list = [user] * len(x_smooth)

        x_smooth = pd.Series(x_smooth, name='date_as_num_smooth')

        y_smooth = pd.Series(y_smooth, name='time_as_num_smooth')

        users = pd.Series(user_list, name='User')

        df = pd.concat([users, x_smooth, y_smooth], axis=1)

        # Joins dfs together to make one big one

        df_smooth = pd.concat([df_smooth, df])

    fig = sns.lineplot(data=df_smooth,
                       x='date_as_num_smooth',
                       y='time_as_num_smooth',
                       hue='User',
                       palette=palette).set(
        xlabel='Date',
        ylabel='Mean time /min')

    ax.yaxis_date()

    ax.set_yticks(y_axis_time_2_mins)

    ax.set_yticklabels(y_axis_time_2_mins)

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    # Formats df

    df_monthly_mean_time = time_delta_as_num_to_time(df_monthly_mean_time)

    df_monthly_mean_time['Date'] = df_monthly_mean_time['timestamp'].dt.strftime('%B %Y')

    df_monthly_mean_time = df_monthly_mean_time[['User', 'Date', 'Time']]

    df_monthly_mean_time = df_monthly_mean_time.rename(columns={'Time': 'Monthly Mean Time'})

    return df_monthly_mean_time, ax.figure


def combined_weekly_mean(df, palette, selected_users):
    """Plots weekly mean times for every player over time on the same lineplot"""

    # Creates df

    df_weekly_mean_time = df.groupby(["User", df["timestamp"].dt.to_period('W')])["time_delta_as_num"].mean()

    df_weekly_mean_time = df_weekly_mean_time.reset_index()

    # Generates 25 mins for y-axis

    y_axis_time = y_axis_generator(25, 'm')

    # Displays every 2 mins

    y_axis_time_num_2_mins = y_axis_time[::2]

    fig, ax = plt.subplots(figsize=(15, 7))

    # Smoothing function doesn't like that Sal only has a month of data so has to be removed

    df_weekly_mean_time = df_weekly_mean_time[df_weekly_mean_time['User'] != 'Sal']

    # Smooths lines out for each user and plots them

    df_smooth = pd.DataFrame()

    for User in selected_users:
        df_weekly_mean_time_rough = df_weekly_mean_time[df_weekly_mean_time['User'] == User]

        x_smooth, y_smooth = savgol_smooth(df_weekly_mean_time_rough)

        # converts x_smooth, y_smooth into a dataframe with user value associated with them

        user_list = [User] * len(x_smooth)

        x_smooth = pd.Series(x_smooth, name='date_as_num_smooth')

        y_smooth = pd.Series(y_smooth, name='time_as_num_smooth')

        users = pd.Series(user_list, name='User')

        df = pd.concat([users, x_smooth, y_smooth], axis=1)

        # Concats dfs together to make one big one

        df_smooth = pd.concat([df_smooth, df])

    # Plotting

    fig = sns.lineplot(data=df_smooth,
                       x='date_as_num_smooth',
                       y='time_as_num_smooth',
                       hue='User',
                       palette=palette).set(
        xlabel='Date',
        ylabel='Mean time /min')

    ax.yaxis_date()

    ax.set_yticks(y_axis_time_num_2_mins)

    ax.set_yticklabels(y_axis_time_num_2_mins)

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    # Formats df

    df_weekly_mean_time = time_delta_as_num_to_time(df_weekly_mean_time)

    df_weekly_mean_time['Date'] = df_weekly_mean_time['timestamp'].dt.strftime('%d %B %Y')

    df_weekly_mean_time = df_weekly_mean_time[['User', 'Date', 'Time']]

    df_weekly_mean_time = df_weekly_mean_time.rename(columns={'Time': 'Weekly Mean Time'})

    return df_weekly_mean_time, ax.figure


def sub_time_boxplot(df, palette):
    """Plots boxplot of submission times"""

    fig, ax = plt.subplots(figsize=(15, 7))

    fig = sns.boxplot(data=df,
                      x="User",
                      y=df["sub_time_delta_as_num"],
                      palette=palette).set(
        ylabel='Time of Submission',
        xlabel=None)

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    ax.set_ylim(ymin=0)

    return ax.figure


def sub_time_violin_plot(df, palette):
    """Plots violin plot of submission times"""

    # Generates 24 hours for y axis

    y_axis_time = y_axis_generator(24, 'h')

    # selects every 2 hours

    y_axis_time_2_hourly = y_axis_time[::2]

    fig, ax = plt.subplots(figsize=(15, 7))

    fig = sns.violinplot(data=df,
                         x="User",
                         y=df["sub_time_delta_as_num"],
                         cut=0,
                         bw=0.25,
                         palette=palette)

    ax.yaxis_date()

    ax.set_yticks(y_axis_time_2_hourly)

    ax.set_yticklabels(y_axis_time_2_hourly)

    ax.set_xlabel(None)

    ax.set_ylabel('Time of Submission')

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    ax.set_ylim(ymin=0)

    return ax.figure


def sub_time_distplot(df, palette, user):
    """Plots dist plot for submission times based on user"""

    df_time_dist = df[df["User"] == user]

    df_time_dist = df_time_dist.sort_values(by='sub_time_delta_as_num')

    fig, ax = plt.subplots(figsize=(15, 7))

    plt.xlim(0, 1)

    fig = sns.distplot(df_time_dist,
                       x=df_time_dist['sub_time_delta_as_num'],
                       bins=30,
                       kde=True,
                       color=palette[user]).set(
        title=user,
        xlabel='Time of Submission')

    ax.xaxis_date()

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    return ax.figure


def hardest_puzzles(df):
    """Plots a scatterplot of 20 dates which have the highest mean time across all users"""

    # Creates df

    df_hardest = df.copy()

    df_hardest['date'] = df_hardest['timestamp'].dt.date

    df_hardest = df_hardest.groupby(['date'])['time_delta_as_num'].mean()

    df_hardest = df_hardest.reset_index()

    df_hardest = df_hardest.sort_values(by='time_delta_as_num', ascending=False)

    # Selects 20 hardest

    df_hardest = df_hardest[:20]

    df_hardest['time'] = mdates.num2timedelta(df_hardest['time_delta_as_num'])

    fig, ax = plt.subplots(figsize=(10, 5))

    fig = sns.scatterplot(data=df_hardest,
                          x='date',
                          y='time_delta_as_num')

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    ax.set_title('20 Hardest Puzzles')

    ax.set_xlabel(None)

    ax.set_ylabel('Mean Time /mins')

    ax.set_ylim(ymin=0)

    # Formats df

    df_hardest = time_delta_as_num_to_time(df_hardest)

    df_hardest = df_hardest[['date', 'Time']]

    df_hardest = df_hardest.sort_values(by='date')

    df_hardest = df_hardest.rename(columns={'date': 'Date'})

    return df_hardest, ax.figure


def easiest_puzzles(df):
    """Plots a scatterplot of 20 dates which have the lowest mean time across all users"""

    df_easiest = df.copy()

    df_easiest['date'] = df_easiest['timestamp'].dt.date

    df_easiest = df_easiest.groupby(['date'])['time_delta_as_num'].mean()

    df_easiest = df_easiest.reset_index()

    df_easiest = df_easiest.sort_values(by='time_delta_as_num', ascending=True)

    # Selects 20 easiest

    df_easiest = df_easiest[:20]

    df_easiest['time'] = mdates.num2timedelta(df_easiest['time_delta_as_num'])

    fig, ax = plt.subplots(figsize=(10, 5))

    fig = sns.scatterplot(data=df_easiest,
                          x='date',
                          y='time_delta_as_num')

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    ax.set_title('20 easiest Puzzles')

    ax.set_xlabel(None)

    ax.set_ylabel('Mean Time /mins')

    ax.set_ylim(ymin=0)

    # Formats df

    df_easiest = time_delta_as_num_to_time(df_easiest)

    df_easiest = df_easiest[['date', 'Time']]

    df_easiest = df_easiest.sort_values(by='date')

    df_easiest = df_easiest.rename(columns={'date': 'Date'})

    return df_easiest, ax.figure


def add_bg_from_local():
    """Creates background for streamlit from image"""

    image_file = r'media/plusword_background.jpg'

    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
        unsafe_allow_html=True
    )

def welcome_gif():
    file_ = open(r'media/completion-animation.gif', 'rb')
    contents = file_.read()
    data_url = base64.b64encode(contents).decode('utf-8')
    file_.close()

    st.markdown(
        f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
        unsafe_allow_html=True,
    )
def user_multi_select(df):
    """Creates multiselect box containing unique users names. Filters df to only contain those users"""

    sorted_unique_user= sorted(df['User'].unique())

    selected_users = st.sidebar.multiselect('User', sorted_unique_user, sorted_unique_user)

    df = df[df['User'].isin(selected_users)]

    return df

def date_select(df):
    """Creates date picker and returns df filtered to be between those dates"""

    start_date=st.sidebar.date_input('Start date', datetime.datetime(2022, 6, 1))

    end_date = st.sidebar.date_input('End date', datetime.date.today())

    df['date'] = df['timestamp'].dt.date

    df = df[(df['date'] > start_date) & (df['date'] <= end_date)]

    return df
