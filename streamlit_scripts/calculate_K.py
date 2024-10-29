#!/user/bin/env python3
# -*- coding: utf-8 -*-
import math
from scipy.constants import h, k
import pandas as pd
import numpy as np
import streamlit as st

#!/user/bin/env python3
# -*- coding: utf-8 -*-
import math
from scipy.constants import h, k
import numpy as np

def cal_Debye_T(df):
    B="Bulk modulus (GPa)"
    G="Shear modulus (GPa)"
    Va = "Speed of sound (m s-1)"
    density = "Density (g cm-3)"
    L="Sound velocity of the longitude wave (m s-1)"
    T="Sound velocity of the transverse wave (m s-1)"
    V = "Volume (Å3)"
    Debye="Acoustic Debye Temperature (K)"
    Vl = ((df[B] + 4 * df[G] / 3) / df[density]) ** 0.5
    Vt = (df[G]/ df[density]) ** 0.5
    Vs = ((1 / pow(Vl, 3) + 2 / pow(Vt, 3)) / 3) ** (-1 / 3)
    df[L]=Vl*1000
    df[T]=Vt*1000
    df[Va] = Vs * 1000
    df[Debye] = h / k * np.power(3 / (4 * math.pi * np.array(df[V])), 1 / 3) * np.array(df[Va])*math.pow(10,10)
    return df
def cal_gamma(df):
    gamma = "Grüneisen parameter"
    Vp = "Poisson ratio"
    L="Sound velocity of the longitude wave (m s-1)"
    T="Sound velocity of the transverse wave (m s-1)"
    a=df[L]/df[T]
    df[Vp] = (pow(a, 2) - 2 ) / (2*pow(a, 2) - 2)
    df[gamma] = 3 * (1 + df[Vp]) / (2 * (2 - 3 * df[Vp]))
    return df

def cal_A(df,n):
    gamma = "Grüneisen parameter"
    A="A"
    if n==1:
        df[A]=2.43e-8/(1-0.514/df[gamma]+0.228/pow(df[gamma],2))
    else:
        df[A] = 1 / (1 +1 / df[gamma] + 8.3e5 / pow(df[gamma], 2.4))
    return df

def cal_K_Slack(df):
    A="A"
    M="the total atomic mass (amu)"
    N = "Number of Atoms"
    Debye = "Acoustic Debye Temperature (K)"
    V="Volume (Å3)"
    gamma = "Grüneisen parameter"
    T=300
    K_Slack="Kappa_Slack (W m-1 K-1)"
    df[K_Slack]=df[A]*df[M]*pow(df[V],1/3)*pow(df[Debye],3)/(pow(df[gamma],2)*T*df[N])*100
    print(df)
    return(df)


def by_MTP(df):
    '''

    :param df: dataframe包括["Bulk modulus", "Grüneisen parameter", "Shear modulus", "Volume", "N","Density"]
    :return: 更新后的dataframe
    '''
    G="Shear modulus (GPa)"
    Va="Speed of sound (m s-1)"
    V="Volume (Å3)"
    N="Number of Atoms"
    T=300
    K_form="Kappa_cal (W m-1 K-1)"
    gamma="Grüneisen parameter"
    try:
        # 分子项
        numerator=df[G]*df[Va]*pow(df[V],1/3)
        # 分母项
        denominator = df[N] * T
        coe_formula=df[gamma].apply(lambda x: math.exp(-x))
        K_formula=numerator/denominator*coe_formula/10
        ato_number = df[N]
        df[N]=ato_number
        df["T"] = 300
        # df[KL] = df[KL].apply(lambda x: '%.2f' % x)
        df[K_form] = K_formula
        # df[K_form] = df[K_form].apply(lambda x: '%.2f' % x)
        # format = lambda x: '%.2f' % x
        # df = df.map(format)
    except Exception as e:
        st.write(e)
    return df

if __name__=="__main__":
    pass
