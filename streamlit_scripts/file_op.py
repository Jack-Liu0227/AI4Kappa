#!/user/bin/env python3
# -*- coding: utf-8 -*-
import os
import io
import glob
import pandas as pd
import streamlit as st
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.io.cif import CifWriter

def process_and_save_uploaded_files(uploaded_files, root_dir_path):
    """
    处理并保存上传的文件，将结构转换为primitive格式。

    :param uploaded_files: 上传的文件列表
    :param root_dir_path: 保存文件的根目录路径
    :return: 字典，键为文件名，值为对应的primitive结构对象
    """
    # 确保目录存在
    if not os.path.exists(root_dir_path):
        os.makedirs(root_dir_path)
    
    # 用于存储转换后的结构
    primitive_structures = {}
        
    # 保存上传的文件，转换为primitive格式
    for uploaded_file in uploaded_files:
        try:
            # 首先将上传的文件内容读入内存
            file_content = io.BytesIO(uploaded_file.getvalue())
            
            # 使用pymatgen解析结构
            structure = Structure.from_file(file_content)
            
            # 获取primitive结构
            analyzer = SpacegroupAnalyzer(structure)
            primitive_structure = analyzer.get_primitive_standard_structure()
            
            # 保存结构对象到字典
            file_name = uploaded_file.name
            primitive_structures[file_name] = primitive_structure
            
            # 创建CIF writer并保存文件
            writer = CifWriter(primitive_structure, symprec=0.1)
            save_path = os.path.join(root_dir_path, file_name)
            writer.write_file(save_path)
            
        except Exception as e:
            print(f"Error processing {uploaded_file.name}: {str(e)}")
            # 如果转换失败，保存原始文件
            save_path = os.path.join(root_dir_path, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getvalue())
    
    # 将结构字典保存到session state中
    st.session_state.primitive_structures = primitive_structures
    return primitive_structures

def is_valid_cif(file_path):
    """检查CIF文件是否有效"""
    try:
        structure = Structure.from_file(file_path)
        print(f"Valid CIF file: {os.path.basename(file_path)}")
        return True
    except Exception as e:
        print(f"Invalid CIF file {os.path.basename(file_path)}: {str(e)}")
        return False

def get_crystalline_data(structure):
    """获取晶体的数据"""
    try:
        data = {}
        data["Number of Atoms"] = len(structure.sites)
        data["Density (g cm-3)"] = structure.density
        data["Volume (Å3)"] = structure.volume
        data["the total atomic mass (amu)"] = sum([site.specie.atomic_mass for site in structure.sites])
        return data
    except Exception as e:
        print(f"Error in get_crystalline_data: {str(e)}")
        return None

def get_dir_crystalline_data(root_dir_path):
    """获取目录下所有晶体的数据（primitive结构）"""
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
                file_name = os.path.basename(cif_path)
                print(f"\nProcessing file: {file_name}")
                
                # 优先从session state获取primitive结构
                if hasattr(st.session_state, 'primitive_structures') and file_name in st.session_state.primitive_structures:
                    primitive_structure = st.session_state.primitive_structures[file_name]
                else:
                    # 如果session state中没有，则重新读取并转换
                    structure = Structure.from_file(cif_path)
                    analyzer = SpacegroupAnalyzer(structure)
                    primitive_structure = analyzer.get_primitive_standard_structure()
                
                data = get_crystalline_data(primitive_structure)
                
                if data is not None:
                    data_list.append(data)
                    file_names.append(file_name)
                    print(f"Successfully processed {file_name}")
                else:
                    print(f"Failed to extract data from {file_name}")
                    
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
        # 从文件名获取对应的primitive结构
        file_name = os.path.basename(cif_path)
        if hasattr(st.session_state, 'primitive_structures') and file_name in st.session_state.primitive_structures:
            primitive_structure = st.session_state.primitive_structures[file_name]
        else:
            # 如果session state中没有，则重新读取并转换
            structure = Structure.from_file(cif_path)
            analyzer = SpacegroupAnalyzer(structure)
            primitive_structure = analyzer.get_primitive_standard_structure()
        
        # 获取晶格参数
        lattice = primitive_structure.lattice
        cell_params = {
            '_cell_length_a': lattice.a,
            '_cell_length_b': lattice.b,
            '_cell_length_c': lattice.c,
            '_cell_angle_alpha': lattice.alpha,
            '_cell_angle_beta': lattice.beta,
            '_cell_angle_gamma': lattice.gamma
        }
        
        # 获取空间群信息
        spacegroup_info = primitive_structure.get_space_group_info()
        
        content = f"""
        <p style='font-size: 18px;'>
        Formula: {primitive_structure.composition.formula}<br>
        Space group: {spacegroup_info[0]} ({spacegroup_info[1]})<br>
        _cell_length_a     {cell_params['_cell_length_a']:.8f}<br>
        _cell_length_b     {cell_params['_cell_length_b']:.8f}<br>
        _cell_length_c     {cell_params['_cell_length_c']:.8f}<br>
        _cell_angle_alpha  {cell_params['_cell_angle_alpha']:.8f}<br>
        _cell_angle_beta   {cell_params['_cell_angle_beta']:.8f}<br>
        _cell_angle_gamma  {cell_params['_cell_angle_gamma']:.8f}<br>
        </p>
        """
        return content
        
    except Exception as e:
        print(f"Error getting crystalline content: {str(e)}")
        return "Error: Could not extract crystal structure information"

def create_id_prop(root_dir_path):
    """创建id_prop.csv文件并返回cif文件路径列表"""
    try:
        # 获取所有cif文件
        cif_path_list = glob.glob(os.path.join(root_dir_path, '*.cif'))
        if not cif_path_list:
            print(f"No CIF files found in {root_dir_path}")
            return [], []
        
        # 获取文件名列表
        cif_name_list = [os.path.basename(path) for path in cif_path_list if os.path.exists(path)]
        
        if not cif_name_list:
            print("No valid CIF files found")
            return [], []
        
        # 创建DataFrame并保存
        df = pd.DataFrame({'name': cif_name_list, 'target': 0})
        csv_path = os.path.join(root_dir_path, 'id_prop.csv')
        df.to_csv(csv_path, index=False)
        print(f"Created id_prop.csv with {len(cif_name_list)} entries")
        
        return cif_path_list, cif_name_list
    except Exception as e:
        print(f"Error creating id_prop.csv: {str(e)}")
        return [], []

def del_cif_file(path):
    """删除CIF和相关临时文件"""
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if file.lower().endswith('.cif') or file == "id_prop.csv" or file == "pre-trained.pth.tar" or file == "test_results.csv":
            os.remove(file_path)

def del_temp_file(path):
    """删除临时文件"""
    test_results = os.path.join(path, "test_results.csv")
    if os.path.exists(test_results):
        os.remove(test_results)

def clean_root_dir(root_dir_path):
    """清理root_dir目录，只保留atom_init.json文件"""
    try:
        for file_path in glob.glob(os.path.join(root_dir_path, '*')):
            if os.path.basename(file_path) != 'atom_init.json':
                os.remove(file_path)
                print(f"Removed: {file_path}")
    except Exception as e:
        print(f"Error cleaning root_dir: {e}")


