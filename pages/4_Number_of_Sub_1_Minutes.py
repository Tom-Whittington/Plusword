import streamlit as st
from plotting_streamlit import data_import, settings, number_of_sub_1_minnies, add_bg_from_local

# Gets default settings
palette, window_days = settings()

# Imports data
df = data_import()

# Gets dataframe and plot
df_sub_minnies, fig = number_of_sub_1_minnies(df, palette)

# Sets background
add_bg_from_local()

# Sets title
st.title('Number of Sub 1-Minute Times')

# Displays plot
st.pyplot(fig)

# Displays dataframe
st.dataframe(df_sub_minnies.set_index('User'), width=800)

