import streamlit as st
from plotting_streamlit import data_import, settings, user_multi_select, combined_period_mean,  add_bg_from_local

# Gets default settings
palette, window_days = settings()

# Imports data
df = data_import()

# Selects users to display
df = user_multi_select(df)

smooth = st.sidebar.checkbox('Smooth Data')

# Sets background
add_bg_from_local()

# Selects chart type
chart_type = st.sidebar.radio(label = 'Select chart type',
                      options=["Monthly Mean", 'Weekly Mean', 'Rolling Average'])

# Selects monthly mean times
if chart_type == 'Monthly Mean':

    # Sets value for amount of smoothing
    poly_value = st.sidebar.slider('Polynomial value',
                                   min_value=2,
                                   max_value=40,
                                   value=40,
                                   help='Higher values give smoother lines, lower values give rougher lines')
    time_period = 'M'

    df, fig = combined_period_mean(df, palette, poly_value, time_period, smooth)

# Selects weekly mean times
elif chart_type == 'Weekly Mean':

    # Sets value for amount of smoothing
    poly_value = st.sidebar.slider('Polynomial value',
                           min_value=1,
                           max_value=10,
                           value=10,
                           help='Higher values give smoother lines, lower values give rougher lines')
    time_period = 'W'

    df, fig = combined_period_mean(df, palette, poly_value, time_period, smooth)

else:
    window_days = st.sidebar.slider('Window Days',
                           min_value=1,
                           max_value=150,
                           value=60,
                           help='Number of days over which to average times')


    #df, fig = df_rolling_average(df, palette, window_days)

# Sets title
st.title(chart_type)

# Display plot
st.pyplot(fig)

# Displays dataframe
st.dataframe(df.set_index('User'), width=800)