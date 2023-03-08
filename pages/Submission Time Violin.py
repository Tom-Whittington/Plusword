import streamlit as st
from plotting_streamlit import data_import, data_cleaning_and_prep, settings, sub_time_violin_plot

palette, figsize, user, window_days = settings()

df = data_import()

df = data_cleaning_and_prep(df)

fig = sub_time_violin_plot(df, palette)

st.title('Submission Time Dist Plot')

st.pyplot(fig)



