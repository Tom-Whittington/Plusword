import streamlit as st
from datetime import date
from plotting_streamlit import data_import, format_for_streamlit, palette_import, include_mums, settings, number_of_submissions,\
    number_of_sub_1_minnies, add_bg_from_local

# Imports default settings
settings()

# Imports data
df = data_import()
df = format_for_streamlit(df)
palette = palette_import()
df = include_mums(df)

#df = df.loc[(df['Timestamp'].date == date.today())]

df.columns = df.columns.str.capitalize()

#st.dataframe(df.set_index('User'), width=800)