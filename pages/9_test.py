import streamlit as st
from plotting_streamlit import data_import, format_for_streamlit, palette_import, add_bg_from_local, user_multi_select, date_select, \
    include_mums, old_data_import

# Imports data
df_new = data_import()
df_new = format_for_streamlit(df_new)

df_old = old_data_import()

# Sets background
add_bg_from_local()

# Sets title
st.title('Data display')

# Displays dataframe
st.dataframe(df_new[['Time', 'User']], width=800)
st.dataframe(df_new.dtypes)
st.dataframe(df_old, width=800)
st.dataframe(df_old.dtypes)


# # Writes number of rows in database
# st.write(str(df.shape[0]) + ' rows found')
