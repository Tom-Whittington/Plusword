import streamlit as st
from plotting_streamlit import data_import, data_cleaning_and_prep, settings, combined_monthly_mean_lineplot, add_bg_from_local, _max_width_

palette, figsize, user, window_days = settings()

df = data_import()

df = data_cleaning_and_prep(df)

sorted_unique_user= sorted(df['User'].unique())

selected_users = st.sidebar.multiselect('User', sorted_unique_user, sorted_unique_user)

df_monthly_mean_time, fig = combined_monthly_mean_lineplot(df, palette, selected_users)

st.title('Monthly Mean Times')

_max_width_()

st.pyplot(fig)

st.dataframe(df_monthly_mean_time.set_index('User'), width=800)

add_bg_from_local()