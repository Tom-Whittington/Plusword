import streamlit as st
from plotting_streamlit import data_import, settings, user_multi_select, combined_monthly_mean_lineplot, combined_weekly_mean, add_bg_from_local

# Gets default settings
palette, window_days = settings()

# Imports data
df = data_import()

# Selects users to display
df = user_multi_select(df)

# Gets dataframe and plot
df_monthly_mean_time, fig = combined_monthly_mean_lineplot(df, palette)

# Sets background
add_bg_from_local()

chart_type = st.sidebar.radio(label = 'Select chart type',
                      options=["Monthly Mean", 'Weekly Mean', 'Rolling Average'])

if chart_type == 'Monthly mean':
    # df, fig = combined_monthly_mean_lineplot(df, palette)
    pass

elif chart_type == 'Weekly Mean':
    poly_value = st.sidebar.slider('Polynomial value',
                           min_value=1,
                           max_value=10,
                           value=10,
                           help='Higher values give smoother lines, lower values give rougher lines')

    #df, fig = combined_weekly_mean(df, palette, poly_value)

elif chart_type =='Rolling Average':
    window_days = st.sidebar.slider('Window Days',
                           min_value=1,
                           max_value=150,
                           value=60,
                           help='Number of days over which to average times')
    # df, fig = df_rolling_average(df, palette, window_days)

# Sets title
st.title(chart_type)

# Display plot
st.pyplot(fig)

# Displays dataframe
st.dataframe(df_monthly_mean_time.set_index('User'), width=800)