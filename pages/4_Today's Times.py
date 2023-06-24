import streamlit as st
from plotting_streamlit import data_import, format_for_streamlit, palette_import, settings, add_bg_from_local, mum_selector, today_times

# Imports default settings
settings()

include_mums = mum_selector()

# Imports data
df = data_import(include_mums)
df = format_for_streamlit(df)
palette = palette_import()

# Sets background
add_bg_from_local()


df, fig = today_times(df, include_mums)


# Sets title
st.title('Today\'s Times')

# Display plot
st.pyplot(fig)

# Displays dataframe
df.columns = df.columns.str.capitalize()
st.dataframe(df.set_index('User'), width=800)