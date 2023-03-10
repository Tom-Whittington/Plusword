import streamlit as st
from plotting_streamlit import data_import, settings, overall_times, add_bg_from_local

# Gets default settings
palette = settings()

# Imports data
df = data_import()

# Sets background
add_bg_from_local()

# Selects chart type
chart_type = st.sidebar.radio(label='Select chart type',
                              options=["Mean", 'Quickest', 'Slowest'])

if chart_type == 'Mean':
    agg = 'Mean'
    df, fig = overall_times(df, palette, agg)

elif chart_type == 'Quickest':
    agg = 'Min'
    df, fig = overall_times(df, palette, agg)

else:
    agg = 'Max'
    df, fig = overall_times(df, palette, agg)

# Sets title
st.title('Overall ' + chart_type + ' Times')

# Display plot
st.pyplot(fig)

# Displays dataframe
st.dataframe(df.set_index('User'), width=800)
