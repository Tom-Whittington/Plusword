import streamlit as st
from plotting_streamlit import add_bg_from_local, welcome_gif

# Sets title
st.title('Welcome')

# Loads gif
welcome_gif()

# Sets background
add_bg_from_local()