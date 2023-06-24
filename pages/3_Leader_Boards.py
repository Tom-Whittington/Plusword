import streamlit as st
from plotting_streamlit import data_import, format_for_streamlit, palette_import, mum_selector, settings, number_of_submissions,\
    number_of_sub_1_minnies, add_bg_from_local

# Imports default settings
settings()

include_mums = mum_selector()

# Imports data
df = data_import(include_mums)
df = format_for_streamlit(df)
palette = palette_import()

# Sets background
add_bg_from_local()

# Selects chart type
chart_type = st.sidebar.radio(label='Select chart type',
                              options=["Sub Minnies", 'Total Submissions'])



if chart_type == 'Sub Minnies':
    df, fig = number_of_sub_1_minnies(df, palette)

else:
    df, fig = number_of_submissions(df, palette)

# Sets title
st.title(chart_type)

# Display plot
st.pyplot(fig)

# Displays dataframe
df.columns = df.columns.str.capitalize()
st.dataframe(df.set_index('User'), width=800)
