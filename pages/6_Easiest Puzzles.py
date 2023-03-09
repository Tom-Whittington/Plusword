import streamlit as st
from plotting_streamlit import data_import, settings, easiest_puzzles, add_bg_from_local

# Gets default settings
palette, window_days = settings()

# Imports data
df = data_import()

# Gets dataframe and plot
df_easiest, fig = easiest_puzzles(df)

# Sets background
add_bg_from_local()

# Sets title
st.title('Easiest Puzzles')

# Display plot
st.pyplot(fig)

# Displays dataframe
st.dataframe(df_easiest.set_index('Date'), width=800)
