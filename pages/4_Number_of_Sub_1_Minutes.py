import streamlit as st
from plotting_streamlit import data_import, data_cleaning_and_prep, settings, number_of_sub_1_minnies, add_bg_from_local

palette, figsize, user, window_days = settings()

df = data_import()

df = data_cleaning_and_prep(df)

df_sub_minnies, fig = number_of_sub_1_minnies(df, palette)


st.title('Number of Sub 1-Minute Times')

st.pyplot(fig)

st.dataframe(df_sub_minnies.set_index('User'), width=800)

add_bg_from_local()