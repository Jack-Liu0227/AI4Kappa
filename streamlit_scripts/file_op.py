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

    # 确保目录存在
    if not os.path.exists(root_dir_path):
        os.makedirs(root_dir_path)
        
    # 保存上传的文件，保持原始文件名格式
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name  # 直接使用原始文件名，不做转换
        save_path = os.path.join(root_dir_path, file_name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getvalue())

def is_valid_cif(file_path):
    """检查CIF文件是否有效"""
    try:
        from pymatgen.core import Structure
        structure = Structure.from_file(file_path)
        print(f"Valid CIF file: {os.path.basename(file_path)}")
        return True
    except Exception as e:
        print(f"Invalid CIF file {os.path.basename(file_path)}: {str(e)}")
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

def get_crystalline_data(structure):
    """获取晶体的数据"""
    try:
        import numpy as np
        from pymatgen.analysis.elasticity.strain import DeformedStructureSet
        from pymatgen.analysis.elasticity.stress import Stress
        from pymatgen.analysis.elasticity.elastic import ElasticTensor
        from pymatgen.analysis.elasticity import Deformation
        
        print("Processing structure:", structure.composition.formula)
        
        # 获取基本属性
        data = {}
        data["Number of Atoms"] = len(structure.sites)
        data["Density (g cm-3)"] = structure.density
        data["Volume (Å3)"] = structure.volume
        data["the total atomic mass (amu)"] = sum([site.specie.atomic_mass for site in structure.sites])
        
        print("Basic properties extracted successfully")
        return data
        
    except Exception as e:
        print(f"Error in get_crystalline_data: {str(e)}")
        return None

def get_dir_crystalline_data(root_dir_path):
    """获取目录下所有晶体的数据"""
    import os
    import glob
    import pandas as pd
    from pymatgen.core import Structure
    
    try:
        # 获取所有cif文件
        cif_path_list = glob.glob(os.path.join(root_dir_path, '*.cif'))
        if not cif_path_list:
            print(f"No CIF files found in {root_dir_path}")
            return pd.DataFrame()
            
        print(f"Found {len(cif_path_list)} CIF files")
        
        data_list = []
        file_names = []
        
        for cif_path in cif_path_list:
            try:
                print(f"\nProcessing file: {os.path.basename(cif_path)}")
                structure = Structure.from_file(cif_path)
                data = get_crystalline_data(structure)
                
                if data is not None:
                    data_list.append(data)
                    file_names.append(os.path.basename(cif_path))
                    print(f"Successfully processed {os.path.basename(cif_path)}")
                else:
                    print(f"Failed to extract data from {os.path.basename(cif_path)}")
                    
            except Exception as e:
                print(f"Error processing {os.path.basename(cif_path)}: {str(e)}")
                continue
                
        if not data_list:
            print("No valid crystal data found")
            return pd.DataFrame()
            
        # 创建DataFrame
        df = pd.DataFrame(data_list)
        df.index = file_names
        print(f"\nSuccessfully created DataFrame with {len(df)} entries")
        print("DataFrame columns:", df.columns.tolist())
        return df
        
    except Exception as e:
        print(f"Error in get_dir_crystalline_data: {str(e)}")
        return pd.DataFrame()

def get_crystalline_content(cif_path):
    """获取晶体的内容"""
    try:
        from pymatgen.core import Structure
        import re
        
        # 读取CIF文件原始内容
        with open(cif_path, 'r') as f:
            cif_content = f.read()
            
        # 使用正则表达式提取晶胞参数
        cell_params = {}
        params = [
            '_cell_length_a',
            '_cell_length_b',
            '_cell_length_c',
            '_cell_angle_alpha',
            '_cell_angle_beta',
            '_cell_angle_gamma'
        ]
        
        for param in params:
            match = re.search(f"{param}\s+(\d+\.?\d*)", cif_content)
            if match:
                cell_params[param] = float(match.group(1))
                
        # 使用pymatgen获取其他信息
        structure = Structure.from_file(cif_path)
        spacegroup_info = structure.get_space_group_info()
        
        content = f"""
        <p style='font-size: 18px;'>
        Formula: {structure.composition.formula}<br>
        Space group: {spacegroup_info[0]} ({spacegroup_info[1]})<br>
        _cell_length_a     {cell_params.get('_cell_length_a', 'N/A'):.8f}<br>
        _cell_length_b     {cell_params.get('_cell_length_b', 'N/A'):.8f}<br>
        _cell_length_c     {cell_params.get('_cell_length_c', 'N/A'):.8f}<br>
        _cell_angle_alpha  {cell_params.get('_cell_angle_alpha', 'N/A'):.8f}<br>
        _cell_angle_beta   {cell_params.get('_cell_angle_beta', 'N/A'):.8f}<br>
        _cell_angle_gamma  {cell_params.get('_cell_angle_gamma', 'N/A'):.8f}<br>
        </p>
        """
        print(f"Successfully extracted content from {os.path.basename(cif_path)}")
        return content
        
    except Exception as e:
        print(f"Error getting crystalline content: {str(e)}")
        return "Error: Could not extract crystal structure information"

def create_id_prop(root_dir_path):
    """创建id_prop.csv文件并返回cif文件路径列表"""
    import os
    import glob
    import pandas as pd
    
    # 检查目录是否存在
    if not os.path.exists(root_dir_path):
        print(f"Directory not found: {root_dir_path}")
        return [], []
    
    # 获取所有cif文件
    cif_path_list = glob.glob(os.path.join(root_dir_path, '*.cif'))
    if not cif_path_list:
        print(f"No CIF files found in {root_dir_path}")
        return [], []
    
    # 获取文件名列表
    cif_name_list = []
    for cif_path in cif_path_list:
        if os.path.exists(cif_path):
            cif_name = os.path.basename(cif_path)
            cif_name_list.append(cif_name)
            print(f"Found CIF file: {cif_name}")
        else:
            print(f"File not found: {cif_path}")
    
    if not cif_name_list:
        print("No valid CIF files found")
        return [], []
    
    try:
        # 创建DataFrame
        df = pd.DataFrame()
        df['name'] = cif_name_list
        df['target'] = 0
        
        # 保存CSV文件
        csv_path = os.path.join(root_dir_path, 'id_prop.csv')
        df.to_csv(csv_path, index=False)
        print(f"Created id_prop.csv with {len(cif_name_list)} entries")
        
        return cif_path_list, cif_name_list
    except Exception as e:
        print(f"Error creating id_prop.csv: {str(e)}")
        return [], []

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

