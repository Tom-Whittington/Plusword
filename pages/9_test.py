import streamlit as st
from plotting_streamlit import data_import, format_for_streamlit, palette_import, add_bg_from_local, user_multi_select, date_select, \
    include_mums

# Imports data
df = data_import()
df = format_for_streamlit(df)

# Sets background
add_bg_from_local()

# Sets title
st.title('Data display')

# Displays dataframe
st.dataframe(df[['Time', 'User']], width=800)
st.dataframe(df, width=800)
st.dataframe(df.dtypes)

# Writes number of rows in database
st.write(str(df.shape[0]) + ' rows found')
