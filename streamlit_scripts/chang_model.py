#!/user/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Zhibin Gao's Group. All rights reserved.
# Author: Zhibin Gao
# Email: zhibin.gao@xjtu.edu.cn
import os
import shutil
import pandas as pd
import streamlit as st
import numpy as np

def copy_model(model_path, sour_path):
    """
    Copy model file to target path
    """
    try:
        import shutil
        import os
        target_path = os.path.join(sour_path, "pre-trained.pth.tar")
        if os.path.exists(model_path):
            shutil.copy2(model_path, target_path)
            print(f"Model copied to {target_path}")
            return True
    except Exception as e:
        print(f"Error copying model: {e}")
        return False

def clean_model(sour_path):
    """
    Delete used pre-trained model files
    """
    try:
        import os
        target_path = os.path.join(sour_path, "pre-trained.pth.tar")
        if os.path.exists(target_path):
            os.remove(target_path)
            print(f"Removed {target_path}")
    except Exception as e:
        print(f"Error removing model: {e}")

def get_model_path(model_path):
    """
    Get model paths and name lists
    """
    import os
    import glob
    model_path_list = glob.glob(os.path.join(model_path, '*-pre-trained.pth.tar'))
    model_name_list = []
    for model_path in model_path_list:
        model_name = os.path.basename(model_path).split('-pre-trained.pth.tar')[0]
        model_name_list.append(model_name)
    return model_path_list, model_name_list

def get_pre_dataframe(results_csv_path, model_name):
    """
    Get prediction results dataframe and convert the third column to powers of 10
    Delete the CSV file after reading
    """
    import pandas as pd
    import numpy as np
    import os
    
    try:
        # Read CSV file
        test_results = pd.read_csv(results_csv_path, header=None)
        test_results.columns = ["ID", "RAND", model_name]
        
        # Remove .cif extension from ID column
        test_results["ID"] = test_results["ID"].apply(lambda x: os.path.splitext(x)[0])
        
        # Convert third column to powers of 10
        test_results[model_name] = np.power(10, test_results[model_name])
        
        # Select required columns and set index
        test_results_p = test_results.iloc[:, [0, 2]]
        test_results_p.set_index("ID", inplace=True)
        
        print(f"Processed data for {model_name}:")
        print(test_results_p.head())
        
        # Delete CSV file
        try:
            if os.path.exists(results_csv_path):
                os.remove(results_csv_path)
                print(f"Removed {results_csv_path}")
        except Exception as e:
            print(f"Error removing {results_csv_path}: {e}")
        
        return test_results_p
        
    except Exception as e:
        print(f"Error in get_pre_dataframe: {str(e)}")
        return pd.DataFrame()

if __name__=="__main__":
    path=r"D:\pycharm\Thermo_Conductivity_APP\model"
    new_path=r"D:\pycharm\Thermo_Conductivity_APP"
    model_path_list,model_name_list=get_model_path(path)
    print(model_path_list,model_name_list)
    for model_path, model_name in zip(model_path_list, model_name_list):
    # Your code here using model_path and model_name
        copy_model(model_path,new_path)
