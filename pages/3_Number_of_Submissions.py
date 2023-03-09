import streamlit as st
from plotting_streamlit import data_import, settings, number_of_submissions, add_bg_from_local

# Imports default settings
palette, window_days = settings()

# Imports data
df = data_import()

# Gets dataframe and plot
df_overall_number_submissions, fig = number_of_submissions(df, palette)

# Sets background
add_bg_from_local()

# Sets title
st.title('Number of Submissions Barchart')

# Display plot
st.pyplot(fig)

# Displays dataframe
st.dataframe(df_overall_number_submissions.set_index('User'), width=800)

