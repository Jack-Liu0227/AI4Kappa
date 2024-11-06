#!/user/bin/env python3
# -*- coding: utf-8 -*-
import os
import streamlit as st
from multipage import MultiPage
from Pages import KappaMTP, KappaP, home, CustomKappa
import streamlit_scripts.file_op as fo

st.set_page_config(page_title="Lattice Thermal Conductivity APP", page_icon=":evergreen_tree:", layout="wide")
st.title('Lattice Thermal Conductivity APP')

# Initialize session state
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = None
if 'root_dir_path' not in st.session_state:
    st.session_state.root_dir_path = os.path.join(os.path.abspath('.'), "root_dir")

# Clean root_dir directory, only keep atom_init.json
fo.clean_root_dir(st.session_state.root_dir_path)

# File upload section
uploaded_files = st.sidebar.file_uploader("Please upload your CIF files", ['cif', 'CIF'], accept_multiple_files=True)
if uploaded_files:
    st.session_state.uploaded_files = uploaded_files
    # Process uploaded files
    fo.process_and_save_uploaded_files(uploaded_files, st.session_state.root_dir_path)
    
    # Display uploaded file information in the top right of the main area
    with st.sidebar.expander("Uploaded Files", expanded=True):
        # Display filenames in list format
        for i, file in enumerate(uploaded_files, 1):
            st.write(f"{i}. {file.name} ✓")
    
    # Display upload success message in main area
    col1, col2 = st.columns([3, 1])
    with col2:
        st.success(f"{len(uploaded_files)} files uploaded successfully!")

app = MultiPage()

# add applications
app.add_page('Home', home.app)
app.add_page("KappaP", KappaP.app)
app.add_page("KappaMTP", KappaMTP.app)
app.add_page("Custom Kappa", CustomKappa.app)

# Run application
if __name__ == '__main__':
    app.run()