import streamlit as st
from plotting_streamlit import data_import, data_cleaning_and_prep, settings, combined_weekly_mean, add_bg_from_local, _max_width_
# Gets default settings
palette, figsize, user, window_days = settings()
# Imports data
df = data_import()

df = data_cleaning_and_prep(df)

sorted_unique_user= sorted(df['User'].unique())

selected_users = st.sidebar.multiselect('User', sorted_unique_user, sorted_unique_user)
# Gets plot
df_weekly_mean_time, fig = combined_weekly_mean(df, palette, selected_users)

# Sets background
add_bg_from_local()
# Sets title
st.title('Weekly Mean Times')
# Display plot
st.pyplot(fig)
# Displays dataframe
st.dataframe(df_weekly_mean_time.set_index('User'), width=800)

add_bg_from_local()