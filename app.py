#!/user/bin/env python3
# -*- coding: utf-8 -*-
import os
import streamlit as st
from multipage import MultiPage
from Pages import KappaP, home, AI4Kappa
import streamlit_scripts.file_op as fo

st.set_page_config(page_title="Lattice Thermal Conductivity APP", page_icon=":evergreen_tree:", layout="wide")
st.title('Lattice Thermal Conductivity APP')

# 初始化session state
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = None
if 'root_dir_path' not in st.session_state:
    st.session_state.root_dir_path = os.path.join(os.path.abspath('.'), "root_dir")

# 文件上传部分
uploaded_files = st.sidebar.file_uploader("Please upload your CIF files", ['cif'], accept_multiple_files=True)
if uploaded_files:
    st.session_state.uploaded_files = uploaded_files
    # 处理上传的文件
    fo.process_and_save_uploaded_files(uploaded_files, st.session_state.root_dir_path)

app = MultiPage()

# add applications
app.add_page('Home', home.app)
app.add_page("KappaP", KappaP.app)
app.add_page("AI4Kappa", AI4Kappa.app)

# Run application
if __name__ == '__main__':
    app.run()