#!/user/bin/env python3
# -*- coding: utf-8 -*-
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
import predict

import streamlit as st
import pandas as pd
from pymatgen.core import Structure
import numpy as np

def display_results_kappap(df):
    formula = r"$$\kappa_L=A\frac{M V^{\frac{1}{3}} \theta_a^3}{\gamma^2 T n} $$"
    try:
        template = f"""
                The number of atoms of the crystal structure is {df["Number of Atoms"].iloc[0]}.<br>
                The volume of the crystal structure is {df["Volume (Å3)"].iloc[0]} Å$^3$.<br>
                The total atomic mass of the crystal structure is {df["the total atomic mass (amu)"].iloc[0]} amu.<br>
                The Bulk modulus of the crystal structure is {df["Bulk modulus (GPa)"].iloc[0]} GPa.<br>
                The Shear modulus of the crystal structure is {df["Shear modulus (GPa)"].iloc[0]} GPa.<br>
                The sound velocity of the crystal structure is {df["Speed of sound (m s-1)"].iloc[0]} m/s.<br>
                The Acoustic Debye Temperature  of the crystal structure is {df["Acoustic Debye Temperature (K)"].iloc[0]} K.<br>
                The Grüneisen parameter of the crystal structure is {df["Grüneisen parameter"].iloc[0]}.<br>
                The formula of the lattice thermal conductivity is: {formula}.<br>
                The calculated lattice thermal conductivity is {df["Kappa_Slack (W m-1 K-1)"].iloc[0]} W/(m·K).<br>
                """
    except Exception as e:
        st.write(f"Error in display_results_kappap: {e}")
        template = "Error displaying results"
    return template

def display_results_ai4kappa(df):
    formula = r"$$\kappa_L=\frac{G \upsilon_s V^{\frac{1}{3}}}{N T} \cdot e^{-\gamma}$$"
    template = f"""
            The volume of the crystal structure is {df["Volume (Å3)"].iloc[0]} Å$^3$.<br>
            The Bulk modulus of the crystal structure is {df["Bulk modulus (GPa)"].iloc[0]} GPa.<br>
            The Shear modulus of the crystal structure is {df["Shear modulus (GPa)"].iloc[0]} GPa.<br>
            The sound velocity of the crystal structure is {df["Speed of sound (m s-1)"].iloc[0]} m/s.<br>
            The Grunisen parameter of the crystal structure is {df["Grüneisen parameter"].iloc[0]}.<br>
            The formula of the lattice thermal conductivity is: {formula}.<br>
            The calculated lattice thermal conductivity is {df["Kappa_cal (W m-1 K-1)"].iloc[0]} W/(m·K).<br>
            """
    return template
def display_columns(method):
    if method == "KappaP":
        ls = ["Number of Atoms", "Density (g cm-3)", "Volume (Å3)", "the total atomic mass (amu)",
              "Bulk modulus (GPa)", "Shear modulus (GPa)", "Sound velocity of the transverse wave (m s-1)",
              "Sound velocity of the longitude wave (m s-1)", "Speed of sound (m s-1)",
              "Poisson ratio", "Grüneisen parameter", "Acoustic Debye Temperature (K)", "Kappa_Slack (W m-1 K-1)"]
    else:
        ls = ["Number of Atoms", "Density (g cm-3)", "Volume (Å3)", "the total atomic mass (amu)",
              "Bulk modulus (GPa)", "Shear modulus (GPa)", "Sound velocity of the transverse wave (m s-1)",
              "Sound velocity of the longitude wave (m s-1)", "Speed of sound (m s-1)",
              "Poisson ratio", "Grüneisen parameter", "Acoustic Debye Temperature (K)", "Kappa_cal (W m-1 K-1)"]
    return ls

def app():
    st.title("Custom Kappa Calculator")
    sour_path = os.path.abspath('.')
    root_dir_path = st.session_state.root_dir_path
    model_path = os.path.join(sour_path, "model")

    # Select calculation method
    method = st.radio(
        "Select calculation method:",
        ["KappaP", "AI4Kappa"],
        horizontal=True
    )

    if st.session_state.uploaded_files:
        # Limit number of files
        cif_files = glob.glob(os.path.join(root_dir_path, '*.cif'))
        if len(cif_files) > 5:
            st.error("Maximum 5 files allowed. Please upload fewer files.")
            return

        # Create parameter input interface
        st.write("---")
        st.subheader("Custom Parameters Input")
        
        # Store parameters for each file in a dictionary
        file_params = {}
        
        for cif_file in cif_files:
            file_name = os.path.basename(cif_file)
            st.write(f"**Parameters for {file_name}:**")
            col1, col2, col3 = st.columns(3)
            
            # Get current file density
            try:
                structure_df = fo.get_crystalline_data(Structure.from_file(os.path.join(root_dir_path, file_name)))
                density = structure_df.get("Density (g cm-3)")
                if density is None or not isinstance(density, (int, float)):
                    density = 3.0  # Default density value
            except Exception as e:
                print(f"Error reading density for {file_name}: {e}")
                density = 3.0
            
            with col1:
                bulk = st.number_input(
                    "Bulk modulus (GPa)",
                    key=f"bulk_{file_name}",
                    value=None,
                    placeholder="Enter value..."
                )
            with col2:
                shear = st.number_input(
                    "Shear modulus (GPa)",
                    key=f"shear_{file_name}",
                    value=None,
                    placeholder="Enter value..."
                )
            
            # Calculate default Grüneisen parameter value
            default_gruneisen = None
            if bulk is not None and shear is not None and density is not None:
                try:
                    # Convert units: GPa -> Pa (×10⁹)
                    bulk_pa = bulk * 1e9
                    shear_pa = shear * 1e9
                    # Density units: g/cm³ -> kg/m³ (×1000)
                    density_si = density * 1000
                    
                    # Calculate longitudinal and transverse wave velocities (m/s)
                    Vl = ((bulk_pa + 4 * shear_pa / 3) / density_si) ** 0.5
                    Vt = (shear_pa / density_si) ** 0.5
                    
                    # Check if denominator is zero
                    if Vt == 0:
                        st.warning(f"Warning for {file_name}: Cannot calculate Grüneisen parameter - Sound velocity of the transverse wave is zero")
                        default_gruneisen = None
                    else:
                        # Calculate Poisson ratio and Grüneisen parameter
                        a = Vl / Vt
                        poisson = (pow(a, 2) - 2) / (2 * pow(a, 2) - 2)
                        
                        # Check if Poisson ratio would cause division by zero
                        if abs(2 - 3 * poisson) < 1e-10:
                            st.warning(f"Warning for {file_name}: Cannot calculate Grüneisen parameter - Invalid Poisson ratio")
                            default_gruneisen = None
                        else:
                            default_gruneisen = 3 * (1 + poisson) / (2 * (2 - 3 * poisson))
                            
                            # Validate calculation result
                            if not (0 < default_gruneisen < 10):  # Grüneisen parameter typically between 0 and 10
                                st.warning(f"Warning for {file_name}: Calculated Grüneisen parameter ({default_gruneisen:.4f}) is out of reasonable range (0-10)")
                                default_gruneisen = None
                
                except ZeroDivisionError:
                    st.warning(f"Warning for {file_name}: Cannot calculate Grüneisen parameter - Division by zero error")
                    default_gruneisen = None
                except Exception as e:
                    st.warning(f"Warning for {file_name}: Error calculating Grüneisen parameter - {str(e)}")
                    default_gruneisen = None
            
            with col3:
                # Detect if Bulk or Shear modulus changed
                current_bulk_shear = f"{bulk}_{shear}"
                if f"prev_bulk_shear_{file_name}" not in st.session_state:
                    st.session_state[f"prev_bulk_shear_{file_name}"] = current_bulk_shear
                
                # Reset user input value if modulus changed
                if current_bulk_shear != st.session_state[f"prev_bulk_shear_{file_name}"]:
                    if f"user_grun_{file_name}" in st.session_state:
                        del st.session_state[f"user_grun_{file_name}"]
                
                # Update previous modulus value
                st.session_state[f"prev_bulk_shear_{file_name}"] = current_bulk_shear
                
                # Get user input value
                user_input = st.text_input(
                    "Grüneisen parameter",
                    key=f"grun_input_{file_name}",
                    value=st.session_state.get(f"user_grun_{file_name}", ""),
                    placeholder="Enter value or leave empty for default"
                )
                
                # Handle user input
                try:
                    if user_input.strip():  # If user entered a value
                        gruneisen = float(user_input)
                        st.session_state[f"user_grun_{file_name}"] = user_input
                    else:  # If input is empty, use default value
                        gruneisen = default_gruneisen
                        if f"user_grun_{file_name}" in st.session_state:
                            del st.session_state[f"user_grun_{file_name}"]
                except ValueError:
                    st.error("Please enter a valid number")
                    gruneisen = None
                
                # Display current value
                if gruneisen is not None:
                    st.write(f"Current value: {gruneisen:.4f}")
                    if user_input.strip():
                        st.write("(User defined)")
                    else:
                        st.write("(Default calculated)")
            
            params = {}
            if bulk is not None:
                params['Bulk modulus (GPa)'] = bulk
            if shear is not None:
                params['Shear modulus (GPa)'] = shear
            if gruneisen is not None:
                params['Grüneisen parameter'] = gruneisen
            
            if params:
                file_params[file_name] = params
                file_params[file_name] = params

        # Calculate button
        calculate = st.button("Calculate")
        if calculate:
            # Check if all required parameters are input
            missing_params = {}
            invalid_params = {}
            
            for file_name, params in file_params.items():
                missing = []
                invalid = []
                
                # Check if required parameters exist
                if 'Bulk modulus (GPa)' not in params:
                    missing.append('Bulk modulus')
                elif params['Bulk modulus (GPa)'] <= 0:
                    invalid.append('Bulk modulus must be positive')
                    
                if 'Shear modulus (GPa)' not in params:
                    missing.append('Shear modulus')
                elif params['Shear modulus (GPa)'] <= 0:
                    invalid.append('Shear modulus must be positive')
                    
                if 'Grüneisen parameter' not in params:
                    missing.append('Grüneisen parameter')
                elif params['Grüneisen parameter'] <= 0:
                    invalid.append('Grüneisen parameter must be positive')
                    
                if missing:
                    missing_params[file_name] = missing
                if invalid:
                    invalid_params[file_name] = invalid
                
            # Display error messages
            if missing_params or invalid_params:
                st.error("Please correct the following errors:")
                
                if missing_params:
                    st.write("Missing parameters:")
                    for file_name, params in missing_params.items():
                        st.write(f"- {file_name}: {', '.join(params)}")
                
                if invalid_params:
                    st.write("Invalid parameters:")
                    for file_name, errors in invalid_params.items():
                        st.write(f"- {file_name}: {', '.join(errors)}")
                
                return
            
            try:
                # Data processing
                all_cry_df = fo.get_dir_crystalline_data(root_dir_path)
                whole_info_df = pd.DataFrame(index=all_cry_df.index, columns=["Number of Atoms", "Density (g cm-3)", "Volume (Å3)", 
                          "the total atomic mass (amu)", "Bulk modulus (GPa)", 
                          "Shear modulus (GPa)", "Grüneisen parameter"])
                
                # Copy basic properties
                for col in ["Number of Atoms", "Density (g cm-3)", "Volume (Å3)", "the total atomic mass (amu)"]:
                    if col in all_cry_df.columns:
                        whole_info_df[col] = all_cry_df[col]

                # Apply user-defined parameters
                for file_name, params in file_params.items():
                    base_name = os.path.splitext(file_name)[0]  # 去掉扩展名
                    if base_name in whole_info_df.index:
                        for param, value in params.items():
                            whole_info_df.loc[base_name, param] = value

                # Get user input Grüneisen parameters
                custom_gamma = whole_info_df["Grüneisen parameter"]
                Debye_df = calk.cal_Debye_T(whole_info_df)

                if method == "KappaP":
                    # Use user input Grüneisen parameters
                    gamma_df = calk.cal_gamma(Debye_df, custom_gamma)
                    A_df = calk.cal_A(gamma_df, 1, custom_gamma)
                    final_df = calk.cal_K_Slack(A_df)
                    display_func = display_results_kappap
                else:  # AI4Kappa
                    gamma_df = calk.cal_gamma(Debye_df, custom_gamma)
                    final_df = calk.by_MTP(gamma_df)
                    display_func = display_results_ai4kappa

                # Display results
                st.write("---")
                st.subheader("Results")
                
                # Display merged dataframe
                st.write("Combined Results:")
                st.dataframe(final_df.loc[:, display_columns(method)])
                
                # Display crystal structure info for each file
                st.write("---")
                st.subheader("Crystal Structure Information")
                
                for file_name in file_params.keys():
                    base_name = os.path.splitext(file_name)[0]  # 去掉扩展名
                    with st.expander(f"Structure details for {file_name}"):
                        cry_content = fo.get_crystalline_content(os.path.join(root_dir_path, file_name))
                        st.write(cry_content, unsafe_allow_html=True)
                        
                        try:
                            # 使用不带扩展名的文件名访问数据
                            file_results = final_df.loc[[base_name]]
                            template = display_func(file_results)
                            st.markdown(template, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error displaying results for {file_name}: {str(e)}")
                        
            except Exception as e:
                st.error(f"An error occurred during calculation: {str(e)}")
                return
        fo.del_cif_file(root_dir_path)
        fo.del_temp_file(sour_path)
    else:
        st.info('Please upload CIF files (maximum 5) in the sidebar first.')

    # Declaration
    declaration = """<p style='font-size: 22px;'>We strive to have clear documentation and examples to help everyone with using our calculator. 
        We will happily fix issues in the documentation and examples should you find any, 
        however, we will not be able to offer extensive user support and training, except for our collaborators.</p>"""
    st.markdown(declaration, unsafe_allow_html=True) 