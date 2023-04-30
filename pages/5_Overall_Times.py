import streamlit as st
from plotting_streamlit import data_import, palette_import, settings, include_mums, overall_times, add_bg_from_local, format_for_streamlit

# Gets default settings
settings()

# Imports data
df = data_import()
df = format_for_streamlit(df)
palette = palette_import()
df = include_mums(df)

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
df.columns = df.columns.str.capitalize()
st.dataframe(df.set_index('User'), width=800)
