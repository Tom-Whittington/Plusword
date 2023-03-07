import streamlit as st
import base64

st.title('Welcome')

st.write('***')

file_ = open(r'media/completion-animation.gif', 'rb')
contents = file_.read()
data_url =base64.b64encode(contents).decode('utf-8')
file_.close()

st.markdown(
    f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
    unsafe_allow_html=True,
)