#!/user/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil
import pandas as pd
import streamlit as st
import numpy as np

def copy_model(model_path, sour_path):
    """
    复制模型文件到目标路径
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
    删除使用过的预训练模型文件
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
    获取模型路径和名称列表
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
    获取预测结果数据框
    """
    import pandas as pd
    test_results = pd.read_csv(results_csv_path, header=None)
    test_results.columns = ["ID", "RAND", model_name]
    test_results_p = test_results.iloc[:, [0, 2]]
    test_results_p.set_index("ID", inplace=True)
    return test_results_p

if __name__=="__main__":
    path=r"D:\pycharm\Thermo_Conductivity_APP\model"
    new_path=r"D:\pycharm\Thermo_Conductivity_APP"
    model_path_list,model_name_list=get_model_path(path)
    print(model_path_list,model_name_list)
    for model_path, model_name in zip(model_path_list, model_name_list):
    # Your code here using model_path and model_name
        copy_model(model_path,new_path)
