import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient
import datetime
import matplotlib.dates as mdates


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


def y_axis_generator(max_y_value, unit):
    """Creates range for y axis from 0 to max_y_value then passes it to time_delta_to_num. Returns y axis values as
    plottable number"""

    y_axis_time_range = list(range(0, max_y_value, 1))

    y_axis_time_delta = pd.to_timedelta(y_axis_time_range, unit=unit)

    y_axis_time_num = time_delta_to_num(y_axis_time_delta)

    return y_axis_time_num

def spline_smooth(df): 
    """Smooths lines via interpolation and splines. Purely cosmetic"""

for user in df['user'].unique():
    
    df_spline =df[df['user'] == user]
    
    x_new = np.linspace(df_plot_spline['date_as_num'].min(), df_plot_spline_['date_as_num'].max(), 50)

    bspline = interpolate.make_interp_spline(df_spline['date_as_num'], df_spline['time_delta_as_num'])

    y_new =bspline(x_new)

    plot = plt.plot(x_new, y_new)
    
return plot


def data_import(connection_string, database_name, collection_name):
    """Connects to database and creates dataframe containing all columns"""

    # point the client at mongo URI

    client = MongoClient(connection_string)

    # select database

    db = client[database_name]

    # select the collection within the database

    test = db.collection_name

    # convert entire collection to Pandas dataframe

    df = pd.DataFrame(list(test.find()))

    return df


def data_cleaning_and_prep(df):
    """ Drops unneeded columns and sets timestamp datatype. Creates submission time from timestamp and converts both
     submission time and completion time to time deltas represented as plottable numbers. Finally, drops submission time
     column as no longer needed"""

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

    return df


def overall_times(df):
    """ Groups all data by user and then finds max, min and mean times for completion time"""

    df_overall_max_time = df.groupby(df["user"])["time_delta_as_num"].max()

    df_overall_max_time = df_overall_max_time.reset_index()

    df_overall_max_time = df_overall_max_time.sort_values(by='time_delta_as_num', ascending=False)

    df_overall_min_time = df.groupby(df["user"])["time_delta_as_num"].min()

    df_overall_min_time = df_overall_min_time.reset_index()

    df_overall_min_time = df_overall_min_time.sort_values(by='time_delta_as_num', ascending=False)

    df_overall_mean_time = df.groupby(df["user"])["time_delta_as_num"].mean()

    df_overall_mean_time = df_overall_mean_time.reset_index()

    return df_overall_max_time, df_overall_min_time, df_overall_mean_time


def number_of_submissions(df):
    """ Counts number of submissions by user and renames columns"""

    df_overall_number_submissions = df["user"].value_counts(sort=True, ascending=False)

    df_overall_number_submissions = df_overall_number_submissions.reset_index()

    df_overall_number_submissions = df_overall_number_submissions.rename(columns={'user': 'Count', 'index': 'user'})

    return df_overall_number_submissions


def number_of_sub_1_minnies(df):
    """ Drops all rows that aren't <1 minute completion time and groups by user"""

    df_sub_minnies = df[df["time_delta"] < datetime.timedelta(minutes=1)]

    df_sub_minnies = df_sub_minnies.groupby(df_sub_minnies["user"])["timestamp"].count()

    df_sub_minnies = df_sub_minnies.reset_index()

    df_sub_minnies = df_sub_minnies.rename(columns={'timestamp': 'count'})

    return df_sub_minnies


def submission_times(df):
    """ Groups all data by user and then finds max, min and mean times for submission time. Mean is the only one worth
    plotting really"""

    df_latest_sub_time = df.groupby(df["user"])["sub_time_delta_as_num"].max()

    df_latest_sub_time = df_latest_sub_time.reset_index()

    df_earliest_sub_time = df.groupby(df["user"])["sub_time_delta_as_num"].min()

    df_earliest_sub_time = df_earliest_sub_time.reset_index()

    df_mean_sub_time = df.groupby(df["user"])["sub_time_delta_as_num"].mean()

    df_mean_sub_time = df_mean_sub_time.reset_index()

    df_mean_sub_time = df_mean_sub_time.sort_values(by='sub_time_delta_as_num', ascending=False)

    return df_latest_sub_time, df_earliest_sub_time, df_mean_sub_time


def monthly_times(df):
    """Groups mean, max and min times for each user by month"""

    df_monthly_mean_time = df.groupby(["user", df["timestamp"].dt.to_period('M')])["time_delta_as_num"].mean()

    df_monthly_mean_time = df_monthly_mean_time.reset_index()

    df_monthly_mean_time["timestamp"] = df_monthly_mean_time["timestamp"].astype('datetime64[M]')

    df_monthly_max_time = df.groupby(["user", df["timestamp"].dt.to_period('M')])["time_delta_as_num"].max()

    df_monthly_max_time = df_monthly_max_time.reset_index()

    df_monthly_max_time["timestamp"] = df_monthly_max_time["timestamp"].astype('datetime64[M]')

    df_monthly_min_time = df.groupby(["user", df["timestamp"].dt.to_period('M')])["time_delta_as_num"].min()

    df_monthly_min_time = df_monthly_min_time.reset_index()

    df_monthly_min_time["timestamp"] = df_monthly_min_time["timestamp"].astype('datetime64[M]')

    return df_monthly_mean_time, df_monthly_max_time, df_monthly_min_time


def weekly_times(df):
    """Groups mean, max and min times for each user by week"""

    df_weekly_mean_time = df.groupby(["user", df["timestamp"].dt.to_period('W')])["time_delta_as_num"].mean()

    df_weekly_mean_time = df_weekly_mean_time.reset_index()

    df_weekly_mean_time["timestamp"] = df_weekly_mean_time["timestamp"].astype('datetime64[W]')

    df_weekly_max_time = df.groupby(["user", df["timestamp"].dt.to_period('W')])["time_delta_as_num"].max()

    df_weekly_max_time = df_weekly_max_time.reset_index()

    df_weekly_max_time["timestamp"] = df_weekly_max_time["timestamp"].astype('datetime64[W]')

    df_weekly_min_time = df.groupby(["user", df["timestamp"].dt.to_period('W')])["time_delta_as_num"].min()

    df_weekly_min_time = df_weekly_min_time.reset_index()

    df_weekly_min_time["timestamp"] = df_weekly_min_time["timestamp"].astype('datetime64[W]')

    return df_weekly_mean_time, df_weekly_max_time, df_weekly_min_time


def rolling_average(df):
    """ Finds rolling average over window_days number of days for each user. Then joins all dataframes together"""

    window_days_str = str(window_days) + 'd'

    df_ra_list = []

    for user in df["user"].unique():
        df_ra = df[df["user"] == user]

        df_ra = df_ra.sort_values(by='timestamp')

        df_ra = df_ra.set_index("timestamp")

        df_ra["time_delta_as_num_RA"] = df_ra["time_delta_as_num"].rolling(window=window_days_str).mean()

        df_ra["time_delta_RA"] = mdates.num2timedelta(df_ra["time_delta_as_num_RA"])

        df_ra = df_ra[['user', 'time_delta_RA', "time_delta_as_num_RA"]]

        df_ra_list.append(df_ra)

    df_ra_finished = pd.concat(df_ra_list)

    df_ra_finished = df_ra_finished.reset_index()

    return df_ra_finished


def overall_max_time_barplot(df_overall_max_time):
    """Barplot showing the longest completion time for each person """

    fig, ax = plt.subplots(figsize=figsize)

    plot = sns.barplot(data=df_overall_max_time,
                       x="user",
                       y="time_delta_as_num",
                       palette=palette).set(
                        title='Slowest Time',
                        ylabel='Time /mins',
                        xlabel=None)

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    plt.show()

    return plot


def overall_min_time_barplot(df_overall_min_time):
    """Barplot showing the shortest completion time for each person """

    fig, ax = plt.subplots(figsize=figsize)

    plot = sns.barplot(data=df_overall_min_time,
                       x="user",
                       y="time_delta_as_num",
                       palette=palette).set(
                        title='Fastest Time',
                        ylabel='Time /mins',
                        xlabel=None)

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    plt.show()

    return plot


def overall_mean_time_barplot(df_overall_mean_time):
    """Barplot showing mean completion time for each person """

    fig, ax = plt.subplots(figsize=figsize)

    plot = sns.barplot(data=df_overall_mean_time,
                       x="user",
                       y="time_delta_as_num",
                       palette=palette).set(
                        title='Mean Time',
                        ylabel='Time /mins',
                        xlabel=None)

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    plt.show()

    return plot


def number_of_sub_1_minnies_barplot(df_sub_minnies):
    """ Barplot of how many sub 1-minute completion times for each person"""

    fig, ax = plt.subplots(figsize=figsize)

    plot = sns.barplot(data=df_sub_minnies,
                       y='count',
                       x='user',
                       palette=palette).set(
                        title='Number of sub 1-minutes',
                        ylabel=None,
                        xlabel=None)

    plt.xticks(rotation=0)

    plt.show()

    return plot


def number_of_submissions_barplot(df_overall_number_submissions):
    """ Barplot of how many submissions total for each person"""

    fig, ax = plt.subplots(figsize=figsize)

    plot = sns.barplot(data=df_overall_number_submissions,
                       y='Count',
                       x='User',
                       palette=palette)

    plt.xticks(rotation=0)

    plt.show()

    return plot


def overall_sub_time_max_barplot(df_latest_sub_time):
    """ Barplot of the latest submission times for each person. Probably not worth plotting"""

    fig, ax = plt.subplots(figsize=figsize)

    plot = sns.barplot(data=df_latest_sub_time,
                       x='user',
                       y='sub_time_delta_as_num',
                       palette=palette).set(
                        title='Latest Time of Submission',
                        ylabel='Time /mins',
                        label=None)

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    plt.show()

    return plot


def overall_sub_time_min_barplot(df_earliest_sub_time):
    """ Barplot of the earliest submission times for each person. Probably not worth plotting"""

    fig, ax = plt.subplots(figsize=figsize)

    plot = sns.barplot(data=df_earliest_sub_time,
                       x='user',
                       y='sub_time_delta_as_num',
                       palette=palette).set(
                        title='Earliest Time of Submission',
                        ylabel='Time /mins',
                        label=None)

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    plt.show()

    return plot


def overall_sub_time_mean_barplot(df_mean_sub_time):
    """ Barplot of mean submission times for each person """

    fig, ax = plt.subplots(figsize=figsize)

    plot = sns.barplot(data=df_mean_sub_time,
                       x='user',
                       y='sub_time_delta_as_num',
                       palette=palette).set(
                        title='Mean Time of Submission',
                        ylabel='Time /mins',
                        label=None)

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    plt.show()

    return plot


def individual_monthly_mean_lineplot(df_monthly_mean_time):
    """Filters out monthly mean time based on value of user. Then plots monthly mean times over time"""

    df_monthly_mean_time_user = df_monthly_mean_time[df_monthly_mean_time['user'] == user]

    fig, ax = plt.subplots(figsize=figsize)

    plot = sns.lineplot(data=df_monthly_mean_time_user,
                        x='timestamp',
                        y='time_delta_as_num',
                        color=palette[user]).set(
                        title=user + '\'s mean times by month',
                        ylabel='Mean time',
                        xlabel='Date')

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    ax.set_ylim(ymin=0)

    plt.show()

    return plot


def combined_monthly_mean_lineplot(df_monthly_mean_time):
    """Plots monthly mean times for every player over time on the same lineplot"""

    # Generates 15 minutes for y axis

    y_axis_time = y_axis_generator(15, 'm')

    # Selects every 2 minutes

    y_axis_time_2_mins = y_axis_time[::2]

    # Plot

    fig, ax = plt.subplots(figsize=figsize)

    plot = sns.lineplot(data=df_monthly_mean_time,
                        x='timestamp',
                        y='time_delta_as_num',
                        hue='user',
                        palette=palette).set(
                        title='Combined Mean Times by month',
                        xlabel='Date',
                        ylabel='Mean time /min')

    ax.yaxis_date()

    ax.set_yticks(y_axis_time_2_mins)

    ax.set_yticklabels(y_axis_time_2_mins)

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    plt.show()

    return plot


def individual_weekly_mean_lineplot(df_weekly_mean_time):
    """Filters out weekly mean time based on value of user. Then plots weekly mean times over time"""

    df_weekly_mean_time_user = df_weekly_mean_time[df_weekly_mean_time['user'] == user]

    fig, ax = plt.subplots(figsize=figsize)

    plot = sns.lineplot(data=df_weekly_mean_time_user,
                        x='timestamp',
                        y='time_delta_as_num',
                        palette=palette).set(
                        title=user + '\'s Mean Times by week',
                        xlabel='Date',
                        ylabel='Mean time /min')

    ax.yaxis_date()

    ax.set_ylim(ymin=0)

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    plt.show()

    return plot


def combined_weekly_mean_lineplot(df_weekly_mean_time):
    """Plots weekly mean times for every player over time on the same lineplot"""

    # Generates 25 mins for y-axis

    y_axis_time = y_axis_generator(25, 'm')

    # Displays every 2 mins

    y_axis_time_num_2_mins = y_axis_time[::2]

    fig, ax = plt.subplots(figsize=figsize)

    plot = sns.lineplot(data=df_weekly_mean_time,
                        x='timestamp',
                        y='time_delta_as_num',
                        hue='user',
                        palette=palette).set(
                        title='Combined Mean Times by week',
                        xlabel='Date',
                        ylabel='Mean time /min')

    ax.yaxis_date()

    ax.set_yticks(y_axis_time_num_2_mins)

    ax.set_yticklabels(y_axis_time_num_2_mins)

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    plt.show()

    return plot


def individual_rolling_average_lineplot(df_ra_finished):
    """Filters out rolling average completion times based on value of user. Plots rolling average over time"""

    df_ra_finished_user = df_ra_finished[df_ra_finished['user'] == user]

    fig, ax = plt.subplots(figsize=figsize)

    plot = sns.lineplot(data=df_ra_finished_user,
                        x='timestamp',
                        y='time_delta_as_num_RA',
                        color=palette[user]).set(
                        title=user + '\'s ' + str(window_days) + 'd' + ' Rolling Mean Times',
                        xlabel='Date',
                        ylabel='Rolling Mean Times /min')

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    ax.set_ylim(ymin=0)

    plt.show()

    return plot


def combined_rolling_average_lineplot(df_ra_finished):
    """Plots rolling average over time for all players"""

    fig, ax = plt.subplots(figsize=figsize)

    plot = sns.lineplot(data=df_ra_finished,
                        x='timestamp',
                        y='time_delta_as_num_RA',
                        hue='user',
                        palette=palette).set(
                        title='Combined ' + str(window_days) + 'd' + ' Rolling Mean Times',
                        xlabel='Date',
                        ylabel='Rolling Mean Times /min')

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    ax.set_ylim(ymin=0)

    plt.show()

    return plot


def sub_time_boxplot(df):
    """Plots boxplot of submission times"""

    fig, ax = plt.subplots(figsize=figsize)

    plot = sns.boxplot(data=df,
                       x="user",
                       y=df["sub_time_delta_as_num"],
                       palette=palette).set(
                        ylabel='Time of Submission',
                        xlabel=None)

    ax.yaxis_date()

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    ax.set_ylim(ymin=0)

    plt.show()

    return plot


def sub_time_violin_plot(df):
    """Plots violin plot of submission times"""

    # Generates 24 hours for y axis

    y_axis_time = y_axis_generator(24, 'h')

    # selects every 2 hours

    y_axis_time_2_hourly = y_axis_time[::2]

    fig, ax = plt.subplots(figsize=figsize)

    plot = sns.violinplot(data=df,
                          x="user",
                          y=df["sub_time_delta_as_num"],
                          cut=0,
                          palette=palette)

    ax.yaxis_date()

    ax.set_yticks(y_axis_time_2_hourly)

    ax.set_yticklabels(y_axis_time_2_hourly)

    ax.set_title('Time of Submission Violin Plot')

    ax.set_xlabel(None)

    ax.set_ylabel('Time of Submission')

    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    ax.set_ylim(ymin=0)

    plt.show()

    return plot


def sub_time_distplot(df):
    """Plots dist plot for submission times based on user"""

    df_time_dist = df[df["user"] == user]

    df_time_dist = df_time_dist.sort_values(by='sub_time_delta_as_num')

    fig, ax = plt.subplots(figsize=figsize)

    plt.xlim(0, 1)

    plot = sns.distplot(df_time_dist,
                        x=df_time_dist['sub_time_delta_as_num'],
                        bins=30,
                        kde=True,
                        color=palette[user]).set(
                        title=user + '\'s Time of Submission distribution',
                        xlabel='Time of Submission')

    ax.xaxis_date()

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    plt.show()

    return plot


# Sets plot style

sns.set_theme()

# Sets colour for each person
global palette={"Sal": "tab:cyan",
                "Joe": "tab:orange",
                "Oli": "tab:purple",
                "Tom": 'tab:pink',
                "George": 'tab:olive',
                "Harvey": "tab:red"}


# Default size of each plot
global figsize=(20, 8)

# Default user for each plot
global user="Tom"

# Default value for rolling average window duration
global window_days = 60

# Database details

connection_string = 'mongodb://localhost:27017'
database_name = 'plusword'
collection_name = 'historical_data'

# Main script

df = data_import(connection_string, database_name, collection_name)

df = data_cleaning_and_prep(df)

df_overall_max_time, df_overall_min_time, df_overall_mean_time = overall_times(df)

df_overall_number_submissions = number_of_submissions(df)

df_sub_minnies = number_of_sub_1_minnies(df)

df_latest_sub_time, df_earliest_sub_time, df_mean_sub_time = submission_times(df)

df_monthly_mean_time, df_monthly_max_time, df_monthly_min_time = monthly_times(df)

df_weekly_mean_time, df_weekly_max_time, df_weekly_min_time = weekly_times(df)

df_ra_finished = rolling_average(df)

overall_max_time_barplot = overall_max_time_barplot(df_overall_max_time)

overall_min_time_barplot = overall_min_time_barplot(df_overall_min_time)

overall_mean_time_barplot = overall_mean_time_barplot(df_overall_mean_time)

number_of_sub_1_minnies_barplot = number_of_sub_1_minnies_barplot(df_sub_minnies)

number_of_submissions_barplot = number_of_submissions_barplot(df_overall_number_submissions)

overall_sub_time_max_barplot = overall_sub_time_max_barplot(df_latest_sub_time)

overall_sub_time_min_barplot = overall_sub_time_min_barplot(df_earliest_sub_time)

overall_sub_time_mean_barplot = overall_sub_time_mean_barplot(df_mean_sub_time)

individual_monthly_mean_lineplot = individual_monthly_mean_lineplot(df_monthly_mean_time)

combined_monthly_mean_lineplot = combined_monthly_mean_lineplot(df_monthly_mean_time)

individual_weekly_mean_lineplot = individual_weekly_mean_lineplot(df_weekly_mean_time)

combined_weekly_mean_lineplot = combined_weekly_mean_lineplot(df_weekly_mean_time)

individual_rolling_average_lineplot = individual_rolling_average_lineplot(df_ra_finished)

combined_rolling_average_lineplot = combined_rolling_average_lineplot(df_ra_finished)

sub_time_boxplot = sub_time_boxplot(df)

sub_time_violin_plot = sub_time_violin_plot(df)

sub_time_distplot = sub_time_distplot(df)
