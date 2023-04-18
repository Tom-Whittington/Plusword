import streamlit as st
from plotting_streamlit import data_import, settings, number_of_submissions, number_of_sub_1_minnies, add_bg_from_local

# Imports default settings
settings()

# Imports data
df, palette = data_import()

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
st.dataframe(df.set_index('User'), width=800)
