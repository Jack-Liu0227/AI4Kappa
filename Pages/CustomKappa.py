#!/user/bin/env python3
# -*- coding: utf-8 -*-
import os
import glob
import sys

# 添加父目录到系统路径
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

    # 选择计算方法
    method = st.radio(
        "Select calculation method:",
        ["KappaP", "AI4Kappa"],
        horizontal=True
    )

    if st.session_state.uploaded_files:
        # 限制文件数量
        cif_files = glob.glob(os.path.join(root_dir_path, '*.cif'))
        if len(cif_files) > 5:
            st.error("Maximum 5 files allowed. Please upload fewer files.")
            return

        # 创建参数输入界面
        st.write("---")
        st.subheader("Custom Parameters Input")
        
        # 使用字典存储每个文件的参数
        file_params = {}
        
        for cif_file in cif_files:
            file_name = os.path.basename(cif_file)
            st.write(f"**Parameters for {file_name}:**")
            col1, col2, col3 = st.columns(3)
            
            # 获取当前文件的密度
            try:
                structure_df = fo.get_crystalline_data(Structure.from_file(os.path.join(root_dir_path, file_name)))
                density = structure_df.get("Density (g cm-3)")
                if density is None or not isinstance(density, (int, float)):
                    density = 3.0  # 默认密度值
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
            
            # 计算默认的 Grüneisen 参数值
            default_gruneisen = None
            if bulk is not None and shear is not None and density is not None:
                try:
                    # 转换单位：GPa -> Pa (×10⁹)
                    bulk_pa = bulk * 1e9
                    shear_pa = shear * 1e9
                    # 密度单位：g/cm³ -> kg/m³ (×1000)
                    density_si = density * 1000
                    
                    # 计算纵波和横波速度 (m/s)
                    Vl = ((bulk_pa + 4 * shear_pa / 3) / density_si) ** 0.5
                    Vt = (shear_pa / density_si) ** 0.5
                    
                    # 检查除数是否为零
                    if Vt == 0:
                        st.warning(f"Warning for {file_name}: Cannot calculate Grüneisen parameter - Sound velocity of the transverse wave is zero")
                        default_gruneisen = None
                    else:
                        # 计算泊松比和Grüneisen参数
                        a = Vl / Vt
                        poisson = (pow(a, 2) - 2) / (2 * pow(a, 2) - 2)
                        
                        # 检查泊松比是否会导致除零
                        if abs(2 - 3 * poisson) < 1e-10:
                            st.warning(f"Warning for {file_name}: Cannot calculate Grüneisen parameter - Invalid Poisson ratio")
                            default_gruneisen = None
                        else:
                            default_gruneisen = 3 * (1 + poisson) / (2 * (2 - 3 * poisson))
                            
                            # 验证计算结果的合理性
                            if not (0 < default_gruneisen < 10):  # Grüneisen参数通常在0到10之间
                                st.warning(f"Warning for {file_name}: Calculated Grüneisen parameter ({default_gruneisen:.4f}) is out of reasonable range (0-10)")
                                default_gruneisen = None
                
                except ZeroDivisionError:
                    st.warning(f"Warning for {file_name}: Cannot calculate Grüneisen parameter - Division by zero error")
                    default_gruneisen = None
                except Exception as e:
                    st.warning(f"Warning for {file_name}: Error calculating Grüneisen parameter - {str(e)}")
                    default_gruneisen = None
            
            with col3:
                # 检测Bulk或Shear模量是否改变
                current_bulk_shear = f"{bulk}_{shear}"
                if f"prev_bulk_shear_{file_name}" not in st.session_state:
                    st.session_state[f"prev_bulk_shear_{file_name}"] = current_bulk_shear
                
                # 如果模量改变，重置用户输入的值
                if current_bulk_shear != st.session_state[f"prev_bulk_shear_{file_name}"]:
                    if f"user_grun_{file_name}" in st.session_state:
                        del st.session_state[f"user_grun_{file_name}"]
                
                # 更新前一个模量值
                st.session_state[f"prev_bulk_shear_{file_name}"] = current_bulk_shear
                
                # 获取用户输入的值
                user_input = st.text_input(
                    "Grüneisen parameter",
                    key=f"grun_input_{file_name}",
                    value=st.session_state.get(f"user_grun_{file_name}", ""),
                    placeholder="Enter value or leave empty for default"
                )
                
                # 处理用户输入
                try:
                    if user_input.strip():  # 如果用户输入了值
                        gruneisen = float(user_input)
                        st.session_state[f"user_grun_{file_name}"] = user_input
                    else:  # 如果输入为空，使用默认值
                        gruneisen = default_gruneisen
                        if f"user_grun_{file_name}" in st.session_state:
                            del st.session_state[f"user_grun_{file_name}"]
                except ValueError:
                    st.error("Please enter a valid number")
                    gruneisen = None
                
                # 显示当前使用的值
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

        # 计算按钮
        calculate = st.button("Calculate")
        if calculate:
            # 检查必要参数是否都已输入
            missing_params = {}
            invalid_params = {}
            
            for file_name, params in file_params.items():
                missing = []
                invalid = []
                
                # 检查必要参数是否存在
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
                
            # 显示错误信息
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
                # 数据处理
                all_cry_df = fo.get_dir_crystalline_data(root_dir_path)
                whole_info_df = pd.DataFrame(index=all_cry_df.index, columns=["Number of Atoms", "Density (g cm-3)", "Volume (Å3)", 
                          "the total atomic mass (amu)", "Bulk modulus (GPa)", 
                          "Shear modulus (GPa)", "Grüneisen parameter"])
                
                # 复制基本属性
                for col in ["Number of Atoms", "Density (g cm-3)", "Volume (Å3)", "the total atomic mass (amu)"]:
                    if col in all_cry_df.columns:
                        whole_info_df[col] = all_cry_df[col]

                # 应用用户自定义参数
                for file_name, params in file_params.items():
                    if file_name in whole_info_df.index:
                        for param, value in params.items():
                            whole_info_df.loc[file_name, param] = value

                # 获取用户输入的Grüneisen参数
                custom_gamma = whole_info_df["Grüneisen parameter"]
                Debye_df = calk.cal_Debye_T(whole_info_df)

                if method == "KappaP":
                    # 使用用户输入的Grüneisen参数
                    gamma_df = calk.cal_gamma(Debye_df, custom_gamma)
                    A_df = calk.cal_A(gamma_df, 1, custom_gamma)
                    final_df = calk.cal_K_Slack(A_df)
                    display_func = display_results_kappap
                else:  # AI4Kappa
                    gamma_df = calk.cal_gamma(Debye_df, custom_gamma)
                    final_df = calk.by_MTP(gamma_df)
                    display_func = display_results_ai4kappa

                # 显示结果
                st.write("---")
                st.subheader("Results")
                
                # 显示合并的数据框
                st.write("Combined Results:")
                st.dataframe(final_df.loc[:, display_columns(method)])
                
                # 显示每个文件的晶体结构信息
                st.write("---")
                st.subheader("Crystal Structure Information")
                
                for file_name in file_params.keys():
                    with st.expander(f"Structure details for {file_name}"):
                        cry_content = fo.get_crystalline_content(os.path.join(root_dir_path, file_name))
                        st.write(cry_content, unsafe_allow_html=True)
                        
                        file_results = final_df.loc[file_name:file_name]
                        template = display_func(file_results)
                        st.markdown(template, unsafe_allow_html=True)
                        
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