import streamlit as st
from plotting_streamlit import data_import, data_cleaning_and_prep, settings, hardest_puzzles, add_bg_from_local

palette, figsize, user, window_days = settings()

df = data_import()

df = data_cleaning_and_prep(df)

df_hardest, fig = hardest_puzzles(df)

st.set_page_config(layout='wide')

st.title('Hardest Puzzles')

st.pyplot(fig)

st.dataframe(df_hardest.set_index('Date'), width=800)

add_bg_from_local()
