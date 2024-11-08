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
    Process and save uploaded files, converting structures to primitive format.

    :param uploaded_files: List of uploaded files
    :param root_dir_path: Root directory path for saving files
    :return: Dictionary with filenames as keys and primitive structure objects as values
    """
    # Ensure directory exists
    if not os.path.exists(root_dir_path):
        os.makedirs(root_dir_path)
    
    # Store converted structures
    primitive_structures = {}
        
    # Save uploaded files and convert to primitive format
    for uploaded_file in uploaded_files:
        try:
            # Get file content as string
            string_data = uploaded_file.getvalue().decode("utf-8")
            
            # Create a StringIO object
            from io import StringIO
            structure_string = StringIO(string_data)
            
            # Parse structure using pymatgen
            structure = Structure.from_str(string_data, fmt="cif")
            
            # Get primitive structure
            primitive_structure = structure.get_primitive_structure()
            
            # Save structure object to dictionary
            file_name = os.path.splitext(uploaded_file.name)[0]  # Remove extension
            primitive_structures[file_name] = primitive_structure
            
            # Create CIF writer and save file
            writer = CifWriter(primitive_structure, symprec=0.1)
            save_path = os.path.join(root_dir_path, uploaded_file.name)
            writer.write_file(save_path)
            
            print(f"Successfully processed {file_name}")
            
        except Exception as e:
            print(f"Error processing {uploaded_file.name}: {str(e)}")
            try:
                # If conversion fails, try to save original file
                save_path = os.path.join(root_dir_path, uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                print(f"Saved original file {uploaded_file.name}")
            except Exception as save_error:
                print(f"Error saving original file {uploaded_file.name}: {str(save_error)}")
    
    # Save structure dictionary to session state
    st.session_state.primitive_structures = primitive_structures
    return primitive_structures

def is_valid_cif(file_path):
    """Check if CIF file is valid"""
    try:
        structure = Structure.from_file(file_path)
        print(f"Valid CIF file: {os.path.basename(file_path)}")
        return True
    except Exception as e:
        print(f"Invalid CIF file {os.path.basename(file_path)}: {str(e)}")
        return False

def get_crystalline_data(structure):
    """Get crystal structure data"""
    try:
        data = {}
        data["Number of Atoms"] = structure.composition.num_atoms
        data["Density (g cm-3)"] = structure.density
        data["Volume (Å3)"] = structure.volume
        data["the total atomic mass (amu)"] = sum([site.specie.atomic_mass for site in structure.sites])
        return data
    except Exception as e:
        print(f"Error in get_crystalline_data: {str(e)}")
        return None

def get_dir_crystalline_data(root_dir_path):
    """Get crystal data for all structures in directory (primitive structures)"""
    try:
        # Get all CIF files
        cif_path_list = glob.glob(os.path.join(root_dir_path, '*.cif'))
        if not cif_path_list:
            print(f"No CIF files found in {root_dir_path}")
            return pd.DataFrame()
            
        print(f"Found {len(cif_path_list)} CIF files")
        
        data_list = []
        file_names = []
        
        for cif_path in cif_path_list:
            try:
                # Get filename without extension
                file_name = os.path.splitext(os.path.basename(cif_path))[0]
                print(f"\nProcessing file: {file_name}")
                
                # First try to get primitive structure from session state
                if hasattr(st.session_state, 'primitive_structures') and file_name in st.session_state.primitive_structures:
                    primitive_structure = st.session_state.primitive_structures[file_name]
                else:
                    # If not in session state, read and convert
                    structure = Structure.from_file(cif_path)
                    primitive_structure = structure.get_primitive_structure()
                
                data = get_crystalline_data(primitive_structure)
                
                if data is not None:
                    data_list.append(data)
                    file_names.append(file_name)  # Use name without extension
                    print(f"Successfully processed {file_name}")
                else:
                    print(f"Failed to extract data from {file_name}")
                    
            except Exception as e:
                print(f"Error processing {os.path.basename(cif_path)}: {e}")
                continue
                
        if not data_list:
            print("No valid crystal data found")
            return pd.DataFrame()
            
        # Create DataFrame with filenames without extensions
        df = pd.DataFrame(data_list)
        df.index = file_names
        print(f"\nSuccessfully created DataFrame with {len(df)} entries")
        print("DataFrame columns:", df.columns.tolist())
        return df
        
    except Exception as e:
        print(f"Error in get_dir_crystalline_data: {str(e)}")
        return pd.DataFrame()

def get_crystalline_content(cif_path):
    """Get crystal structure content"""
    try:
        # Get primitive structure from filename
        file_name = os.path.basename(cif_path)
        if hasattr(st.session_state, 'primitive_structures') and file_name in st.session_state.primitive_structures:
            primitive_structure = st.session_state.primitive_structures[file_name]
        else:
            # If not in session state, read and convert
            structure = Structure.from_file(cif_path)
            analyzer = SpacegroupAnalyzer(structure)
            primitive_structure = analyzer.get_primitive_standard_structure()
        
        # Get lattice parameters
        lattice = primitive_structure.lattice
        cell_params = {
            '_cell_length_a': lattice.a,
            '_cell_length_b': lattice.b,
            '_cell_length_c': lattice.c,
            '_cell_angle_alpha': lattice.alpha,
            '_cell_angle_beta': lattice.beta,
            '_cell_angle_gamma': lattice.gamma
        }
        
        # Get space group info
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
    """Create id_prop.csv file and return list of CIF file paths"""
    try:
        # Get all CIF files
        cif_path_list = glob.glob(os.path.join(root_dir_path, '*.[cC][iI][fF]'))
        if not cif_path_list:
            print(f"No CIF files found in {root_dir_path}")
            return [], []
        
        # Get list of filenames
        cif_name_list = [os.path.basename(path) for path in cif_path_list if os.path.exists(path)]
        
        if not cif_name_list:
            print("No valid CIF files found")
            return [], []
        
        # Create DataFrame and save
        df = pd.DataFrame({'name': cif_name_list, 'target': 0})
        csv_path = os.path.join(root_dir_path, 'id_prop.csv')
        df.to_csv(csv_path, index=False)
        print(f"Created id_prop.csv with {len(cif_name_list)} entries")
        
        return cif_path_list, cif_name_list
    except Exception as e:
        print(f"Error creating id_prop.csv: {str(e)}")
        return [], []

def del_cif_file(path):
    """Delete CIF and related temporary files"""
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if file.lower().endswith('.cif') or file == "id_prop.csv" or file == "pre-trained.pth.tar" or file == "test_results.csv":
            os.remove(file_path)

def del_temp_file(path):
    """Delete temporary files"""
    test_results = os.path.join(path, "test_results.csv")
    if os.path.exists(test_results):
        os.remove(test_results)

def clean_root_dir(root_dir_path):
    """Clean root_dir directory, keeping only atom_init.json file"""
    try:
        for file_path in glob.glob(os.path.join(root_dir_path, '*')):
            if os.path.basename(file_path) != 'atom_init.json':
                os.remove(file_path)
                print(f"Removed: {file_path}")
    except Exception as e:
        print(f"Error cleaning root_dir: {e}")

