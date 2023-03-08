import datetime
import streamlit as st
from plotting_streamlit import data_import, data_cleaning_and_prep, settings, add_bg_from_local


palette, figsize, user, window_days = settings()

df = data_import()
df = data_cleaning_and_prep(df)

st.title('Data display')

df_streamlit = df.copy()

sorted_unique_user= sorted(df_streamlit['User'].unique())

selected_users = st.sidebar.multiselect('User', sorted_unique_user, sorted_unique_user)

start_date=st.sidebar.date_input('Start date', datetime.datetime(2022, 6, 1))

end_date = st.sidebar.date_input('End date', datetime.date.today())

df_streamlit['date'] = df_streamlit['timestamp'].dt.date

df_streamlit = df_streamlit[df_streamlit['User'].isin(selected_users)]

df_streamlit = df_streamlit[(df_streamlit['date'] > start_date) & (df_streamlit['date'] <= end_date)]

df_streamlit.columns = df_streamlit.columns.str.capitalize()

df_streamlit=df_streamlit.set_index('Timestamp')

df_streamlit = df_streamlit.sort_index(ascending=False)

st.write(str(df_streamlit.shape[0]) + ' rows')

st.dataframe(df_streamlit[['Time', 'User']], width=800)

add_bg_from_local()