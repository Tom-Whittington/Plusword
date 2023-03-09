import streamlit as st
from plotting_streamlit import data_import, data_cleaning_and_prep, settings, overall_min_time, add_bg_from_local
# Gets default settings
palette, figsize, user, window_days = settings()
# Imports data
df = data_import()

df = data_cleaning_and_prep(df)
# Gets dataframe and plot
df_overall_min_time, fig = overall_min_time(df, palette)

# Sets background
add_bg_from_local()
# Sets title
st.title('Quickest Times')
# Display plot
st.pyplot(fig)
# Displays dataframe
st.dataframe(df_overall_min_time.set_index('User'), width=800)

add_bg_from_local()



