import streamlit as st
from plotting_streamlit import data_import, settings, hardest_puzzles, add_bg_from_local

# Gets default settings
palette, window_days = settings()

# Imports data
df = data_import()

# Gets dataframe and plot
df_hardest, fig = hardest_puzzles(df)

# Sets background
add_bg_from_local()

# Sets title
st.title('Hardest Puzzles')

# Display plot
st.pyplot(fig)

# Displays dataframe
st.dataframe(df_hardest.set_index('Date'), width=800)
