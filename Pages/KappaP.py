#!/user/bin/env python3
# -*- coding: utf-8 -*-
import os
import warnings
import glob
import io
import sys

# Add parent directory to system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import custom modules
import streamlit_scripts.file_op as fo
import streamlit_scripts.chang_model as cm
import streamlit_scripts.calculate_K as calk
import predict  # Should import correctly now

# Import third party libraries
import streamlit as st
import pandas as pd
from pymatgen.core.structure import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer


def display_results(df):
    """
    Display calculation results
    Args:
        df: DataFrame containing calculation results
    Returns:
        template: HTML template string containing results
    """
    # Define lattice thermal conductivity formula
    formula=r"$$\kappa_L=A\frac{M V^{\frac{1}{3}} \theta_a^3}{\gamma^2 T n} $$"
    try:
        # Generate results display template
        template=f"""
                The number of atoms of the crystal structure is {df["Number of Atoms"][0]}.<br>
                The volume of the crystal structure is {df["Volume (Å3)"][0]} Å$^3$.<br>
                The total atomic mass of the crystal structure is {df["the total atomic mass (amu)"][0]} amu.<br>
                The Bulk modulus of the crystal structure is {df["Bulk modulus (GPa)"][0]} GPa.<br>
                The Shear modulus of the crystal structure is {df["Shear modulus (GPa)"][0]} GPa.<br>
                The sound velocity of the crystal structure is {df["Speed of sound (m s-1)"][0]} m/s.<br>
                The Acoustic Debye Temperature  of the crystal structure is {df["Acoustic Debye Temperature (K)"][0]} K.<br>
                The Grüneisen parameter of the crystal structure is {df["Grüneisen parameter"][0]}.<br>
                The formula of the lattice thermal conductivity is: {formula}.<br>
                The calculated lattice thermal conductivity is {df["Kappa_Slack (W m-1 K-1)"][0]} W/(m·K).<br>
                """
    except Exception as e:
        st.write(e)
    return template


def app():
    """Main application function"""
    # Set page title
    st.title("KappaP")
    # Get paths
    sour_path = os.path.abspath('.')
    root_dir_path = st.session_state.root_dir_path
    model_path = os.path.join(sour_path, "model")

    if st.session_state.uploaded_files:
        # Check if uploaded CIF files are valid and ensure primitive structures are used
        cif_path_list = glob.glob(os.path.join(root_dir_path, '*.cif'))
        valid_structures = {}
        
        for cif_path in cif_path_list:
            try:
                file_name = os.path.basename(cif_path)
                # First try to get converted primitive structure from session state
                if hasattr(st.session_state, 'primitive_structures') and file_name in st.session_state.primitive_structures:
                    valid_structures[file_name] = st.session_state.primitive_structures[file_name]
                    print(f"Using cached primitive structure for {file_name}")
                else:
                    # If not in session state, read and convert
                    structure = Structure.from_file(cif_path)
                    analyzer = SpacegroupAnalyzer(structure)
                    primitive_structure = analyzer.get_primitive_standard_structure()
                    valid_structures[file_name] = primitive_structure
                    print(f"Created new primitive structure for {file_name}")
            except Exception as e:
                st.write(f"{file_name} Invalid CIF file: {str(e)}")
                os.remove(cif_path)
                st.write(f"Invalid CIF file {file_name} has been deleted.")

        if not valid_structures:
            st.error("No valid CIF files found.")
            return

        # Create id_prop.csv
        cif_path_list, cif_name_list = fo.create_id_prop(root_dir_path)
        
        if len(cif_name_list) > 0:
            # Get crystal info for first file
            first_cif_name = cif_name_list[0]
            first_cif_path = os.path.join(root_dir_path, first_cif_name)
            
            # Get crystal info using get_crystalline_content
            cry_content = fo.get_crystalline_content(first_cif_path)
            
            results_csv_path = os.path.join(sour_path, "test_results.csv")
            
            # Get model paths and names
            model_path_list, model_name_list = cm.get_model_path(model_path)
            
            # Predict using first model
            try:
                cm.copy_model(model_path_list[0], sour_path)
                predict.main(root_dir_path)
                pre_df = cm.get_pre_dataframe(results_csv_path, model_name_list[0])
            finally:
                cm.clean_model(sour_path)
                
            # Predict using remaining models and merge results
            for model_path, model_name in zip(model_path_list[1:], model_name_list[1:]):
                try:
                    cm.copy_model(model_path, sour_path)
                    predict.main(root_dir_path)
                    pre_df1 = cm.get_pre_dataframe(results_csv_path, model_name)
                    pre_df = pd.merge(pre_df, pre_df1, left_index=True, right_index=True)
                finally:
                    cm.clean_model(sour_path)
                    
            try:
                st.write("---")
                # Get crystal data
                all_cry_df = fo.get_dir_crystalline_data(root_dir_path)
                if all_cry_df.empty:
                    st.error("Failed to extract crystal data from CIF files.")
                    return
                
                # Merge crystal data and predictions
                whole_info_df = pd.merge(all_cry_df, pre_df, left_index=True, right_index=True)
                if whole_info_df.empty:
                    st.error("Failed to merge crystal data with predictions.")
                    return
                
                # Calculate physical parameters
                Debye_df = calk.cal_Debye_T(whole_info_df)
                gamma_df = calk.cal_gamma(Debye_df)
                A_df = calk.cal_A(gamma_df, 1)
                K_slack_df = calk.cal_K_Slack(A_df)
                
                # Select columns to display
                ls = ["Number of Atoms", "Density (g cm-3)", "Volume (Å3)", "the total atomic mass (amu)",
                      "Bulk modulus (GPa)", "Shear modulus (GPa)", "Sound velocity of the transverse wave (m s-1)",
                      "Sound velocity of the longitude wave (m s-1)", "Speed of sound (m s-1)",
                      "Poisson ratio", "Grüneisen parameter", "Acoustic Debye Temperature (K)", "Kappa_Slack (W m-1 K-1)"]
                final_df = K_slack_df.loc[:, ls]
                
                # Check if results are empty
                if final_df.empty:
                    st.error("No data was generated. Please check your input files.")
                    return
                
                # Display results
                st.dataframe(final_df)
                st.write("---")
                
                # Display filename
                first_index = final_df.index[0] if len(final_df.index) > 0 else "No file"
                st.write(f"The file name of displaying crystalline is: {first_index}")
                
                # Display crystal structure info
                st.write("The information of uploaded crystal structure is:")
                st.write(cry_content, unsafe_allow_html=True)
                st.write("---")
                
                # Display calculation results
                if not final_df.empty:
                    template = display_results(final_df)
                    st.markdown(template, unsafe_allow_html=True)
                st.write("---")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.write("Please check your input files and try again.")
            finally:
                # Clean up temporary files
                fo.del_cif_file(root_dir_path)
                fo.del_temp_file(sour_path)
    else:
        # Prompt user to upload files
        st.info('Please upload CIF files in the sidebar first.')
        
    # Display declaration
    declaration = """<p style='font-size: 22px;'>We strive to have clear documentation and examples to help everyone with using KappaP on their own. 
        We will happily fix issues in the documentation and examples should you find any, 
        however, we will not be able to offer extensive user support and training, except for our collaborators.</p>"""
    st.markdown(declaration, unsafe_allow_html=True)
