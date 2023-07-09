import streamlit as st
from plotting_streamlit import data_import, format_for_streamlit, palette_import, settings, longest_streak, current_streak,\
    add_bg_from_local, user_multi_select_non_mums

# Imports default settings
settings()

# Imports data
df = data_import()
df = format_for_streamlit(df)

# Sets background
add_bg_from_local()

# Selects chart type
chart_type = st.sidebar.radio(label='Select chart type',
                              options= ['Longest Streak', 'Current Streak'])

# Selects users to display
df = user_multi_select_non_mums(df)

if chart_type == 'Longest Streak':
    df, fig = longest_streak(df)

else:
    df, fig = current_streak(df)

# Sets title
st.title(chart_type)

# Display plot
st.pyplot(fig)

# Displays dataframe
df.columns = df.columns.str.capitalize()
st.dataframe(df.set_index('User'), width=800)
