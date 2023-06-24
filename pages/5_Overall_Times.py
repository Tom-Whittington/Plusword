import streamlit as st
from plotting_streamlit import data_import, palette_import, settings, mum_selector, overall_times, add_bg_from_local, format_for_streamlit, user_multi_select

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

# Selects users to display
df = user_multi_select(df)

# Sets title
st.title('Overall ' + chart_type + ' Times')

# Display plot
st.pyplot(fig)

# Displays dataframe
df.columns = df.columns.str.capitalize()
st.dataframe(df.set_index('User'), width=800)
