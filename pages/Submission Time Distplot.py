import streamlit as st
import matplotlib.pyplot as plt
from plotting_streamlit import data_import, data_cleaning_and_prep, settings, sub_time_distplot, add_bg_from_local
# Gets default settings
palette, figsize, user, window_days = settings()
# Imports data
df = data_import()

df = data_cleaning_and_prep(df)

sorted_unique_users= sorted(df['User'].unique())

User = st.sidebar.selectbox('User', sorted_unique_users)
# Gets plot
fig = sub_time_distplot(df, palette, User)

# Sets background
add_bg_from_local()
# Sets title
st.title('Submission Time Violin Plot')
# Display plot
st.pyplot(fig)

add_bg_from_local()



