import streamlit as st
from plotting_streamlit import data_import, format_for_streamlit, settings, number_of_submissions,\
    number_of_sub_1_minnies, add_bg_from_local, user_multi_select_non_mums

# Imports default settings
settings()

# Imports data
df = data_import()
df = format_for_streamlit(df)

# Sets background
add_bg_from_local()

# Selects chart type
chart_type = st.sidebar.radio(label='Select chart type',
                              options=["Sub Minnies", 'Total Submissions'])

# Selects users to display
df = user_multi_select_non_mums(df)


if chart_type == 'Sub Minnies':
    df, fig = number_of_sub_1_minnies(df)

else:
    df, fig = number_of_submissions(df)


# Sets title
st.title(chart_type)

# Display plot
st.pyplot(fig)

# Displays dataframe
df.columns = df.columns.str.capitalize()
st.dataframe(df.set_index('User'), width=800)
