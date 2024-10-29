#!/user/bin/env python3
# -*- coding: utf-8 -*-
import os
import random
import re
import warnings
import shutil
import tempfile
import io
import pandas as pd
import numpy as np
import streamlit as st
from pymatgen.io.cif import CifParser
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.io.cif import CifWriter


def process_and_save_uploaded_files(uploaded_files, root_dir_path):
    """
    处理并保存上传的文件。

    :param uploaded_files: 上传的文件列表
    :param root_dir_path: 保存文件的根目录路径
    """

    for uploaded_file in uploaded_files:
        # 简化文件名处理
        file_name = uploaded_file.name.lower().replace("CIF", "cif")

        # 检查文件扩展名是否为 .cif
        if not file_name.endswith('.cif'):
            st.error(f"Unsupported file type: {file_name}. Only .cif files are accepted.")
            continue

        # 构建保存路径
        save_path = os.path.join(root_dir_path, file_name)

        try:
            # 创建临时文件并将内容写入
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_file_path = temp_file.name

            # 从临时文件加载结构
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                parser = CifParser(temp_file_path)
                structure = parser.get_structures(primitive=True)[0]

            # 获取原始结构
            pri_struct = SpacegroupAnalyzer(structure).get_primitive_standard_structure()

            # 将处理后的结构写回最终文件
            writer = CifWriter(pri_struct)
            writer.write_file(save_path)

            # 成功处理后通知用户
            st.write(f"File saved: {file_name}")

        except Exception as e:
            # 异常处理
            st.error(f"Failed to process file {file_name}: {str(e)}")

        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

def is_valid_cif(file_path):
    try:
        with open(file_path, 'r') as cif_file:
            parser = CifParser(cif_file)
            structure = parser.get_structures()[0]
            return True
    except:
        return False


def parse_formula(formula):
    pattern = re.compile(r'([A-Z][a-z]*)(\d*)')
    matches = pattern.findall(formula)
    elements_dic = {}
    for match in matches:
        element = match[0]
        count = int(match[1]) if match[1] else 1
        elements_dic[element] = count
    return elements_dic

def calculate_molecular_mass(formula, element_mass_dict):
    elements = parse_formula(formula)
    atom_mass = 0.0
    for element, count in elements.items():
        if element in element_mass_dict:
            atom_mass += element_mass_dict[element] * count
        else:
            print(f"Error: Element '{element}' not found in the mass dictionary.")
    return atom_mass

def get_dir_crystalline_data(root_path):
    molarmass = {'H': 1.008, 'He': 4.003, 'Li': 6.941, 'Be': 9.012, 'B': 10.811, 'C': 12.011, 'N': 14.007, 'O': 15.999,
                 'F': 18.998, 'Ne': 20.180
        , 'Na': 22.990, 'Mg': 24.305, 'Al': 26.982, 'Si': 28.086, 'P': 30.974, 'S': 32.065, 'Cl': 35.453, 'Ar': 39.948,
                 'K': 39.098, 'Ca': 40.078
        , 'Sc': 44.956, 'Ti': 47.867, 'V': 50.942, 'Cr': 51.996, 'Mn': 54.938, 'Fe': 55.845, 'Co': 58.933, 'Ni': 58.693,
                 'Cu': 63.546, 'Zn': 65.409
        , 'Ga': 69.723, 'Ge': 72.640, 'As': 74.922, 'Se': 78.960, 'Br': 79.904, 'Kr': 83.798, 'Rb': 85.468,
                 'Sr': 87.620, 'Y': 88.906, 'Zr': 91.224
        , 'Nb': 92.906, 'Mo': 95.940, 'Tc': 97.907, 'Ru': 101.070, 'Rh': 102.906, 'Pd': 106.420, 'Ag': 107.868,
                 'Cd': 112.411, 'In': 114.818, 'Sn': 118.710
        , 'Sb': 121.760, 'Te': 127.600, 'I': 126.904, 'Xe': 131.293, 'Cs': 132.905, 'Ba': 137.327, 'La': 138.906,
                 'Ce': 140.116, 'Pr': 140.908, 'Nd': 144.240
        , 'Pm': 144.910, 'Sm': 150.360, 'Eu': 151.964, 'Gd': 157.250, 'Tb': 158.925, 'Dy': 162.500, 'Ho': 164.930,
                 'Er': 167.259, 'Tm': 168.934, 'Yb': 173.040
        , 'Lu': 174.967, 'Hf': 178.490, 'Ta': 180.948, 'W': 183.840, 'Re': 186.207, 'Os': 190.230, 'Ir': 192.217,
                 'Pt': 195.078, 'Au': 196.967, 'Hg': 200.590
        , 'Tl': 204.383, 'Pb': 207.200, 'Bi': 208.980, 'Po': 208.980, 'At': 209.990, 'Rn': 222.020, 'Fr': 223.020,
                 'Ra': 226.030, 'Ac': 227.030, 'Th': 232.038
        , 'Pa': 231.036, 'U': 238.029, 'Np': 237.050, 'Pu': 244.060, 'Am': 243.060, 'Cm': 247.070, 'Bk': 247.070,
                 'Cf': 251.080, 'Es': 252.080, 'Fm': 257.100
        , 'Md': 258.100, 'No': 259.100, 'Lr': 260.110, 'Rf': 261.110, 'Db': 262.110}
    cif_list=os.listdir(root_path)
    cif_data_dict={"Number of Atoms":2,"Density (g cm-3)":2.28,"Volume (Å3)": 40.89}
    all_cry_df=pd.DataFrame([cif_data_dict],index=["Si"])
    for cif_file in cif_list:
        if cif_file.lower().endswith('.cif'):
            cif_path=os.path.join(root_path,cif_file)
            cif_name=os.path.splitext(cif_file)[0]
            density,volume=np.nan,np.nan
            with open(cif_path,"r") as f:
                line_list=f.readlines()
            for line in line_list:
                cif_data_dict = dict()
                if "volume" in line.lower():
                    pattern = r'\d*\.?\d+'
                    volume = float(re.findall(pattern, line)[0])
                elif "formula_sum" in line.lower():
                    str1="formula_sum"
                    ix=line.find(str1)
                    line=line[ix+len(str1):].replace("'","").replace('"', ' ').strip().split()
                    element_dict=dict()
                    if len(line)>1:
                        atom_num=0
                        for element_number in line:
                            match = re.match(r'([a-zA-Z]+)(\d+)', element_number)
                            if match:
                                element = match.group(1)
                                number = match.group(2)
                                atom_num+=eval(number)
                                element_dict.update({element:eval(number)*molarmass[element]})
                        molar_mass=sum(element_dict.values())
                    else:
                        match = re.match(r'([a-zA-Z]+)(\d+)', line[0])
                        if match:
                            element = match.group(1)
                            number = match.group(2)
                            atom_num = eval(number)
                            element_dict.update({element:eval(number)*molarmass[element]})
                        molar_mass=sum(element_dict.values())
                else:
                    pass
            try:
                density=molar_mass/volume/6.022*10
            except Exception as e:
                st.write(e)
            cif_data_dict.update({"Number of Atoms": atom_num, "Density (g cm-3)": density,"the total atomic mass (amu)":molar_mass,"Volume (Å3)": volume})
            one_cry_df = pd.DataFrame([cif_data_dict], index=[str(cif_name)])
            all_cry_df=pd.concat([all_cry_df,one_cry_df])
    return all_cry_df.iloc[1:,:]

def get_crystalline_content(cif_path):
    with open(cif_path,"r") as f:
        line_list=f.readlines()
    cry_content=[]
    stru_data=[]
    for i in range(len(line_list)):
        if "cell_length" in line_list[i]:
            stru_data.append(line_list[i])
        elif "cell_angle" in line_list[i]:
            stru_data.append(line_list[i])
        elif "space_group_name" in line_list[i]:
            space_g=line_list[i]
            cry_content.append(space_g)
        else:
            pass
    cry_content_list=cry_content+stru_data
    cry_content="<br>".join(cry_content_list)
    return cry_content

def create_id_prop(path):
    file_list = os.listdir(path)
    id_name, properties,cif_path_list = [], [],[]
    for file in file_list:
        if file.lower().endswith('.cif'):
            base_name = os.path.splitext(file)
            id_name.append(base_name[0])
            properties.append(random.randint(0, 1))
            cif_path_list.append(os.path.join(path,file))
        elif file=="atom_init.json" or file=="id_prop.csv":
            pass
        else:
            os.remove(file)
    dic = {'id': id_name, 'properties': properties}
    df = pd.DataFrame(dic)
    csv_path = os.path.join(path,'id_prop.csv')
    try:
        df.to_csv(csv_path, index=False, header=False)
    except Exception as e:
        st.write(e)
    else:
        pass
    return cif_path_list,id_name

def del_cif_file(path):
    file_list = os.listdir(path)
    for file in file_list:
        file_path=os.path.join(path,file)
        if file.lower().endswith('.cif') or file == "id_prop.csv":
            os.remove(file_path)
        elif file=="pre-trained.pth.tar" or file =="test_results.csv":
            os.remove(file_path)
        else:
            pass

def del_temp_file(path):
    file_list = os.listdir(path)
    for file in file_list:
        file_path=os.path.join(path,file)
        # if file=="pre-trained.pth.tar" or file =="test_results.csv":
        if file == "test_results.csv":
            os.remove(file_path)
        else:
            pass

def get_N_cif(m,n,cif_path_dir,root_dir):
    file_list=os.listdir(cif_path_dir)
    for i in range(m-1,n):
        cif_path=os.path.join(cif_path_dir,file_list[i])
        shutil.copy2(cif_path,root_dir)
    return file_list[i]

