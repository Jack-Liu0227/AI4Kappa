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
            with col3:
                gruneisen = st.number_input(
                    "Grüneisen parameter",
                    key=f"grun_{file_name}",
                    value=None,
                    placeholder="Enter value..."
                )
            
            params = {}
            if bulk is not None:
                params['Bulk modulus (GPa)'] = bulk
            if shear is not None:
                params['Shear modulus (GPa)'] = shear
            if gruneisen is not None:
                params['Grüneisen parameter'] = gruneisen
            
            if params:
                file_params[file_name] = params

        # 计算按钮
        calculate = st.button("Calculate")
        if calculate:

            # 数据处理
            all_cry_df = fo.get_dir_crystalline_data(root_dir_path)
            whole_info_df = pd.DataFrame(index=all_cry_df.index, columns=["Number of Atoms", "Density (g cm-3)", "Volume (Å3)", 
                              "the total atomic mass (amu)", "Bulk modulus (GPa)", 
                              "Shear modulus (GPat", "Grüneisen parameter"])
            
            # 复制基本属性
            for col in ["Number of Atoms", "Density (g cm-3)", "Volume (Å3)", "the total atomic mass (amu)"]:
                if col in all_cry_df.columns:
                    whole_info_df[col] = all_cry_df[col]
 

            # 应用用户自定义参数
            for file_name, params in file_params.items():
                if file_name in whole_info_df.index:
                    for param, value in params.items():
                        whole_info_df.loc[file_name, param] = value

            custom_gamma=whole_info_df["Grüneisen parameter"]
            Debye_df = calk.cal_Debye_T(whole_info_df)

            if method == "KappaP":
                # 根据选择的方法进行计算
                
                  # 展示Debye温度计算后的数据
                gamma_df = calk.cal_gamma(Debye_df,custom_gamma)

                A_df = calk.cal_A(gamma_df, 1,custom_gamma)

                final_df = calk.cal_K_Slack(A_df)
                display_func = display_results_kappap
            else:  # AI4Kappa
                gamma_df = calk.cal_gamma(Debye_df,custom_gamma)
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
                    if method == "KappaP":
                        template = display_results_kappap(file_results)
                    else:
                        template = display_results_ai4kappa(file_results)
                    st.markdown(template, unsafe_allow_html=True)
        fo.del_cif_file(root_dir_path)
        fo.del_temp_file(sour_path)
    else:
        st.info('Please upload CIF files (maximum 5) in the sidebar first.')

    # Declaration
    declaration = """<p style='font-size: 22px;'>We strive to have clear documentation and examples to help everyone with using our calculator. 
        We will happily fix issues in the documentation and examples should you find any, 
        however, we will not be able to offer extensive user support and training, except for our collaborators.</p>"""
    st.markdown(declaration, unsafe_allow_html=True) 