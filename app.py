#!/user/bin/env python3
# -*- coding: utf-8 -*-
import os
import streamlit as st
from multipage import MultiPage
from Pages import KappaP, home, AI4Kappa, CustomKappa
import streamlit_scripts.file_op as fo

st.set_page_config(page_title="Lattice Thermal Conductivity APP", page_icon=":evergreen_tree:", layout="wide")
st.title('Lattice Thermal Conductivity APP')

# 初始化session state
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = None
if 'root_dir_path' not in st.session_state:
    st.session_state.root_dir_path = os.path.join(os.path.abspath('.'), "root_dir")

# 清理root_dir目录，只保留atom_init.json
fo.clean_root_dir(st.session_state.root_dir_path)

# 文件上传部分
uploaded_files = st.sidebar.file_uploader("Please upload your CIF files", ['cif'], accept_multiple_files=True)
if uploaded_files:
    st.session_state.uploaded_files = uploaded_files
    # 处理上传的文件
    fo.process_and_save_uploaded_files(uploaded_files, st.session_state.root_dir_path)
    
    # 在主区域右上角显示上传文件信息
    with st.sidebar.expander("Uploaded Files", expanded=True):
        # 使用列表格式显示文件名
        for i, file in enumerate(uploaded_files, 1):
            st.write(f"{i}. {file.name} ✓")
    
    # 在主区域显示上传成功的提示
    col1, col2 = st.columns([3, 1])
    with col2:
        st.success(f"{len(uploaded_files)} files uploaded successfully!")

app = MultiPage()

# add applications
app.add_page('Home', home.app)
app.add_page("KappaP", KappaP.app)
app.add_page("AI4Kappa", AI4Kappa.app)
app.add_page("Custom Kappa", CustomKappa.app)

# Run application
if __name__ == '__main__':
    app.run()