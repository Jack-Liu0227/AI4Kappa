#!/user/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Zhibin Gao's Group. All rights reserved.
# Author: Zhibin Gao
# Email: zhibin.gao@xjtu.edu.cn
import os
import glob
import sys

# Add parent directory to system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import streamlit_scripts.file_op as fo
import streamlit_scripts.chang_model as cm
import streamlit_scripts.calculate_K as calk
import predict  # Should import correctly now

import streamlit as st
import pandas as pd

def display_results(df):
    formula=r"$$\kappa_L=\frac{G \upsilon_s V^{\frac{1}{3}}}{N T} \cdot e^{-\gamma}$$"
    template=f"""
            The volume of the crystal structure is {df["Volume (Å3)"].iloc[0]} Å$^3$.<br>
            The Bulk modulus of the crystal structure is {df["Bulk modulus (GPa)"].iloc[0]} GPa.<br>
            The Shear modulus of the crystal structure is {df["Shear modulus (GPa)"].iloc[0]} GPa.<br>
            The sound velocity of the crystal structure is {df["Speed of sound (m s-1)"].iloc[0]} m/s.<br>
            The Grunisen parameter of the crystal structure is {df["Grüneisen parameter"].iloc[0]}.<br>
            The formula of the lattice thermal conductivity is: {formula}.<br>
            The calculated lattice thermal conductivity is {df["Kappa_cal (W m-1 K-1)"].iloc[0]} W/(m·K).<br>
            """
    return template
def app():
    st.title("Physics-informed machine learning for lattice thermal conductivity (PINK)")
    sour_path = os.path.abspath('.')
    root_dir_path = st.session_state.root_dir_path
    model_path = os.path.join(sour_path, "model")

    if st.session_state.uploaded_files:
        cif_path_list = glob.glob(os.path.join(root_dir_path, '*.cif'))
        for i in range(len(cif_path_list)):
            cif_file_path = cif_path_list[i]
            if fo.is_valid_cif(cif_file_path):
                pass
            else:
                cif_name = os.path.basename(cif_file_path)
                st.write(f"{cif_name} Invalid CIF file with no structures!")
                os.remove(cif_file_path)
                st.write(f"In order to prevent program errors, invalid CIF file {cif_name} has been deleted.")

        cif_path_list, cif_name_list = fo.create_id_prop(root_dir_path)
        if len(glob.glob(os.path.join(root_dir_path, '*.cif'))):
            first_cif_path = cif_path_list[0]
            cry_content = fo.get_crystalline_content(first_cif_path)
            results_csv_path = os.path.join(sour_path, "test_results.csv")
            model_path_list, model_name_list = cm.get_model_path(model_path)
            try:
                cm.copy_model(model_path_list[0], sour_path)
                predict.main(root_dir_path)
                pre_df = cm.get_pre_dataframe(results_csv_path, model_name_list[0])
            finally:
                cm.clean_model(sour_path)  # Clean model files

            for model_path, model_name in zip(model_path_list[1:], model_name_list[1:]):
                try:
                    cm.copy_model(model_path, sour_path)
                    predict.main(root_dir_path)
                    pre_df1 = cm.get_pre_dataframe(results_csv_path, model_name)
                    pre_df = pd.merge(pre_df, pre_df1, left_index=True, right_index=True)
                finally:
                    cm.clean_model(sour_path)  # Clean model files

            try:
                st.write("---")
                all_cry_df = fo.get_dir_crystalline_data(root_dir_path)
                if all_cry_df.empty:
                    st.error("Failed to extract crystal data from CIF files.")
                    return
                    
                whole_info_df = pd.merge(all_cry_df, pre_df, left_index=True, right_index=True)
                if whole_info_df.empty:
                    st.error("Failed to merge crystal data with predictions.")
                    return
                    
                Debye_df = calk.cal_Debye_T(whole_info_df)
                gamma_df = calk.cal_gamma(Debye_df)
                K_df = calk.by_MTP(gamma_df)
                ls = ["Number of Atoms", "Density (g cm-3)", "Volume (Å3)", "the total atomic mass (amu)",
                      "Bulk modulus (GPa)", "Shear modulus (GPa)", "Sound velocity of the transverse wave (m s-1)",
                      "Sound velocity of the longitude wave (m s-1)", "Speed of sound (m s-1)",
                      "Poisson ratio", "Grüneisen parameter", "Acoustic Debye Temperature (K)", "Kappa_cal (W m-1 K-1)"]
                final_df = K_df.loc[:, ls]
                
                # Check to ensure DataFrame is not empty
                if final_df.empty:
                    st.error("No data was generated. Please check your input files.")
                    return
                    
                st.dataframe(final_df)
                st.write("---")
                
                # Safely get index with default value
                first_index = final_df.index[0] if len(final_df.index) > 0 else "No file"
                st.write(f"The file name of displaying crystalline is: {first_index}")
                
                st.write("The information of uploaded crystal structure is:")
                st.write(cry_content, unsafe_allow_html=True)
                st.write("---")
                
                # Only display results if DataFrame is not empty
                if not final_df.empty:
                    template = display_results(final_df)
                    st.markdown(template, unsafe_allow_html=True)
                st.write("---")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.write("Please check your input files and try again.")
            finally:
                # Clean up files
                fo.del_cif_file(root_dir_path)
    else:
        st.info('Please upload CIF files in the sidebar first.')

    with st.container():
        declaration = """<p style='font-size: 22px;'>We strive to have clear documentation and examples to help everyone with using PINK on their own. 
                        We will happily fix issues in the documentation and examples should you find any, 
                        however, we will not be able to offer extensive user support and training, except for our collaborators.</p>"""
        st.markdown(declaration, unsafe_allow_html=True)
