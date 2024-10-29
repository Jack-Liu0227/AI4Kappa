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
            try:
                # 创建id_prop.csv
                cif_path_list, cif_name_list = fo.create_id_prop(root_dir_path)
                
                # 获取预测结果
                results_csv_path = os.path.join(sour_path, "test_results.csv")
                model_path_list, model_name_list = cm.get_model_path(model_path)
                
                try:
                    cm.copy_model(model_path_list[0], sour_path)
                    predict.main(root_dir_path)
                    pre_df = cm.get_pre_dataframe(results_csv_path, model_name_list[0])
                finally:
                    cm.clean_model(sour_path)

                for model_path, model_name in zip(model_path_list[1:], model_name_list[1:]):
                    try:
                        cm.copy_model(model_path, sour_path)
                        predict.main(root_dir_path)
                        pre_df1 = cm.get_pre_dataframe(results_csv_path, model_name)
                        pre_df = pd.merge(pre_df, pre_df1, left_index=True, right_index=True)
                    finally:
                        cm.clean_model(sour_path)

                # 数据处理
                all_cry_df = fo.get_dir_crystalline_data(root_dir_path)
                whole_info_df = pd.merge(all_cry_df, pre_df, left_index=True, right_index=True)

                # 应用用户自定义参数
                for file_name, params in file_params.items():
                    file_mask = whole_info_df.index == file_name
                    for param, value in params.items():
                        whole_info_df.loc[file_mask, param] = value

                # 根据选择的方法进行计算
                Debye_df = calk.cal_Debye_T(whole_info_df)
                
                if method == "KappaP":
                    # 对每个文件分别处理
                    for file_name in file_params.keys():
                        file_mask = Debye_df.index == file_name
                        file_data = Debye_df[file_mask]
                        
                        # 如果有自定义的 Grüneisen parameter，使用它
                        if 'Grüneisen parameter' in file_params[file_name]:
                            gamma = file_params[file_name]['Grüneisen parameter']
                            file_data['Grüneisen parameter'] = gamma
                        else:
                            file_data = calk.cal_gamma(file_data)
                            
                        A_df = calk.cal_A(file_data, 1)
                        if file_name == list(file_params.keys())[0]:
                            final_df = calk.cal_K_Slack(A_df)
                        else:
                            final_df = pd.concat([final_df, calk.cal_K_Slack(A_df)])
                            
                    display_func = display_results_kappap
                else:  # AI4Kappa
                    # 对每个文件分别处理
                    for file_name in file_params.keys():
                        file_mask = Debye_df.index == file_name
                        file_data = Debye_df[file_mask]
                        
                        # 如果有自定义的 Grüneisen parameter，使用它
                        if 'Grüneisen parameter' in file_params[file_name]:
                            gamma = file_params[file_name]['Grüneisen parameter']
                            file_data['Grüneisen parameter'] = gamma
                        else:
                            file_data = calk.cal_gamma(file_data)
                            
                        if file_name == list(file_params.keys())[0]:
                            final_df = calk.by_MTP(file_data)
                        else:
                            final_df = pd.concat([final_df, calk.by_MTP(file_data)])
                            
                    display_func = display_results_ai4kappa

                # 显示结果
                st.write("---")
                st.subheader("Results")
                
                # 显示合并的数据框
                st.write("Combined Results:")
                st.dataframe(final_df)
                
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

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                fo.del_cif_file(root_dir_path)
                fo.del_temp_file(sour_path)
    else:
        st.info('Please upload CIF files (maximum 5) in the sidebar first.')

    # Declaration
    declaration = """<p style='font-size: 22px;'>We strive to have clear documentation and examples to help everyone with using our calculator. 
        We will happily fix issues in the documentation and examples should you find any, 
        however, we will not be able to offer extensive user support and training, except for our collaborators.</p>"""
    st.markdown(declaration, unsafe_allow_html=True) 