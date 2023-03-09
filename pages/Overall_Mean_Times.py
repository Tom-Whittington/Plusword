import streamlit as st
from plotting_streamlit import data_import, settings, overall_mean_time, add_bg_from_local

# Gets default settings
palette, figsize, user, window_days = settings()
# Imports data
df = data_import()

# Gets dataframe and plot
df_overall_mean_time, fig = overall_mean_time(df, palette)

# Sets background
add_bg_from_local()
# Sets title
st.title('Mean Times')
# Display plot
st.pyplot(fig)
# Displays dataframe
st.dataframe(df_overall_mean_time.set_index('User'), width=800)

add_bg_from_local()