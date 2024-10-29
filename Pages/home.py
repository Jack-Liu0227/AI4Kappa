#!/user/bin/env python3
# -*- coding: utf-8 -*-
import os
import streamlit as st
from PIL import Image

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def app():
    sour_path = os.path.abspath('.')
    file_name = os.path.join(sour_path, "style/style.css")
    local_css(file_name)

    # ---- HEADER SECTION ----
    with st.container():
        st.title("Welcome to Lattice Thermal Conductivity Calculator")
        st.subheader("A Powerful Tool for Thermal Conductivity Prediction")
        st.write(
            """
            This application provides two advanced methods for calculating lattice thermal conductivity:
            - **KappaP**: Based on the Slack model
            - **AI4Kappa**: Using machine learning approach
            """
        )

    # ---- METHODS INTRODUCTION ----
    with st.container():
        st.write("---")
        st.header("Our Methods")
        
        # KappaP Method
        st.subheader("KappaP Method")
        st.write(
            """
            KappaP uses the Slack model to calculate lattice thermal conductivity:
            """
        )
        st.latex(r"\kappa_L = A\frac{M V^{1/3} \theta_a^3}{\gamma^2 T n}")
        st.write(
            """
            - Requires crystal structure information (CIF file)
            - Calculates mechanical properties including:
                - Bulk modulus
                - Shear modulus
                - Sound velocity
                - Debye temperature
            """
        )
        
        # AI4Kappa Method
        st.subheader("AI4Kappa Method")
        st.write(
            """
            AI4Kappa employs machine learning for thermal conductivity prediction:
            """
        )
        st.latex(r"\kappa_L = \frac{G v_s V^{1/3}}{N T} \cdot e^{-\gamma}")
        st.write(
            """
            - Requires crystal structure input (CIF file)
            - Predicts properties including:
                - Bulk modulus
                - Shear modulus
                - Sound velocity
                - Grüneisen parameter
            """
        )

    # ---- HOW TO USE ----
    with st.container():
        st.write("---")
        st.header("How to Use")
        st.write(
            """
            1. Select your preferred method (KappaP or AI4Kappa)
            2. Upload your CIF file(s)
            3. Get comprehensive results including:
                - Crystal structure information
                - Mechanical properties
                - Calculated thermal conductivity
            
            Note: Please ensure your CIF files are properly formatted and contain complete structural information.
            """
        )

    # ---- CONTACT ----
    with st.container():
        st.write("---")
        st.header("Contact Us")
        
        contact_info = """
        <p style='font-size: 18px;'>
        If you have any questions or need assistance, please contact us:<br><br>
        
        <b>Principal Investigator:</b><br>
        Prof. Zhibin Gao<br>
        Email: zhibin.gao@xjtu.edu.cn<br>
        Website: <a href="https://gr.xjtu.edu.cn/web/zhibin.gao">https://gr.xjtu.edu.cn/web/zhibin.gao</a><br><br>
        
        <b>Technical Support:</b><br>
        Yujie Liu<br>
        Email: liu_yujie@stu.xjtu.edu.cn
        </p>
        """
        st.markdown(contact_info, unsafe_allow_html=True)

    # ---- DECLARATION ----
    with st.container():
        st.write("---")
        declaration = """
        <p style='font-size: 22px;'>
        We strive to provide clear documentation and examples to help users effectively utilize our thermal conductivity calculation tools. 
        While we are happy to address issues in the documentation and examples, please note that extensive user support 
        and training are primarily available to our collaborators.
        </p>
        """
        st.markdown(declaration, unsafe_allow_html=True)
