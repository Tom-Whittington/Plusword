import streamlit as st
from plotting_streamlit import data_import, data_cleaning_and_prep, settings, number_of_submissions

palette, figsize, user, window_days = settings()

df = data_import()

df = data_cleaning_and_prep(df)

df_overall_number_submissions, fig = number_of_submissions(df, palette)

st.title('Number of Submissions Barchart')

st.pyplot(fig)

st.dataframe(df_overall_number_submissions.set_index('User'), width=800)