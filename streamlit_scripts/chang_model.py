#!/user/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil
import pandas as pd
import streamlit as st
import numpy as np
def copy_all_model(path,new_path):
    model_list=os.scandir(path)
    new_model_path=os.path.join(new_path,"pre-trained.pth.tar")
    for model in model_list:
        model_path=os.path.join(path,model.name)
        shutil.copy(model_path,new_model_path)

def get_model_path(path):
    """

    :param path:
    :return: 目标路径下的所有模型的绝对路径model_path_list,以及模型名字列表
    """
    model_list = os.scandir(path)
    model_path_list = []
    model_name = []
    # new_model_path=os.path.join(new_path,"pre-trained.pth.tar")
    for model in model_list:
        model_path = os.path.join(path, model.name)

        model_name.append(model.name.split("-")[0])
        model_path_list.append(model_path)
        # shutil.copy(model_path,new_model_path)
    return model_path_list, model_name


def copy_model(path,new_path):
    new_model_path=os.path.join(new_path,"pre-trained.pth.tar")
    shutil.copy(path,new_model_path)



def get_pre_dataframe(path,model_name):
    df=pd.read_csv(path,header=None)
    df.columns=["ID","RAND",model_name]
    pre_df=df.iloc[:,2]
    pre_df.index=list(df["ID"].apply(lambda x:str(x)))
    pre_df=np.power(10,pre_df)
    # st.dataframe(pre_df)
    return pre_df



if __name__=="__main__":
    path=r"D:\pycharm\Thermo_Conductivity_APP\model"
    new_path=r"D:\pycharm\Thermo_Conductivity_APP"
    model_path_list,model_name_list=get_model_path(path)
    print(model_path_list,model_name_list)
    for model_path, model_name in zip(model_path_list, model_name_list):
    # Your code here using model_path and model_name
        copy_model(model_path,new_path)
