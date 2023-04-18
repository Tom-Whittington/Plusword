import streamlit as st
from plotting_streamlit import data_import, settings, add_bg_from_local, user_single_select, sub_time_violin_plot, \
    sub_time_distplot, sub_time_boxplot

# Gets default settings
settings()

# Imports data
df, palette = data_import()

# Sets background
add_bg_from_local()

# Selects chart type
chart_type = st.sidebar.radio(label='Select chart type',
                              options=["Violin Plot", 'Dist Plot', 'Box Plot'])

if chart_type == 'Violin Plot':
    fig = sub_time_violin_plot(df, palette)

elif chart_type == 'Dist Plot':

    # Selects users
    df, user = user_single_select(df)
    fig = sub_time_distplot(df, palette, user)

else:
    fig = sub_time_boxplot(df, palette)

# Sets title
st.title('Submission Time ' + chart_type)

# Display plot
st.pyplot(fig)
