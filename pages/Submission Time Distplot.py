import streamlit as st
import matplotlib.pyplot as plt
from plotting_streamlit import data_import, data_cleaning_and_prep, settings, sub_time_distplot, add_bg_from_local

palette, figsize, user, window_days = settings()

df = data_import()

df = data_cleaning_and_prep(df)

sorted_unique_users= sorted(df['User'].unique())

User = st.sidebar.selectbox('User', sorted_unique_users)

fig = sub_time_distplot(df, palette, User)

st.title('Submission Time Violin Plot')

st.pyplot(fig)

add_bg_from_local()



