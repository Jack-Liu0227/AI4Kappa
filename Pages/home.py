#!/user/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Zhibin Gao's Group. All rights reserved.
# Author: Zhibin Gao
# Email: zhibin.gao@xjtu.edu.cn
import os
import streamlit as st
from PIL import Image
import base64
import fitz  # PyMuPDF
import io

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def app():
    # sour_path = os.path.abspath('.')
    # file_name = os.path.join(sour_path, "style/style.css")
    # local_css(file_name)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_name = os.path.join(project_root, "style/style.css")
    if os.path.exists(file_name):
        local_css(file_name)

    # ---- HEADER SECTION ----
    with st.container():
        st.title("Welcome to Lattice Thermal Conductivity Calculator")
        st.subheader("A Powerful Tool for Lattice Thermal Conductivity Prediction")
        st.write(
            """
            Lattice thermal conductivity is a crucial property that determines heat conduction in crystalline materials. 
            This application provides three advanced methods for calculating lattice thermal conductivity:
            - **KappaP**: Based on the Slack model
            - **PINK**: Based on an interpretable formula published in [Materials Today Physics](https://doi.org/10.1016/j.mtphys.2024.101549)
            - **Custom Calculator**: Allows you to input your own elastic parameters and calculate thermal conductivity using both models (up to 5 files)
            """
        )

    # ---- HOW TO USE ----
    with st.container():
        st.write("---")
        st.header("How to Use")
        
        st.write("""
        1. **File Upload**
           - Upload your CIF files using the sidebar
           - Files must be in valid CIF format
        
        2. **Choose Method**
           - KappaP: Traditional Slack model approach
           - MTP: Materials Today Physics model
           - Custom Calculator: Combine both methods with your parameters (maximum 5 files)
        
        3. **Get Results**
           - Comprehensive output including:
             - Lattice thermal conductivity
             - Intermediate parameters
             - Crystal structure details
        """)

    # ---- CALCULATION METHODS ----
    with st.container():
        st.write("---")
        st.header("Calculation Methods")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔬 Physical Model (KappaP)")
            st.write(
                """
                - Based on the Slack model
                - Calculates lattice thermal conductivity using:
                    - Crystal structure parameters
                    - Elastic properties
                    - Thermal properties
                - Provides detailed intermediate results
                - Suitable for fundamental research and materials design
                """
            )
            
            # Display Slack equation
            st.latex(r"\kappa_L = A\frac{M V^{1/3} \theta_a^3}{\gamma^2 T n}")
            
        with col2:
            st.subheader("🤖 PINK Model (Physics Informed Kappa)")
            st.write(
                """
                - Based on Physics Informed Kappa (PINK) model
                - Features:
                    - Fast prediction
                    - Physics-informed approach
                    - Handles complex structures
                - Derived from theoretical analysis in [Materials Today Physics](https://doi.org/10.1016/j.mtphys.2024.101549)
                - Ideal for rapid screening
                """
            )
            # Display MTP equation
            st.latex(r"\kappa_L = \frac{G v_s V^{1/3}}{N T} \cdot e^{-\gamma}")

 

    # ---- CUSTOM CALCULATOR ----
    with st.container():
        st.write("---")
        st.header("Custom Calculator")
        st.write(
            """
            Combine both KappaP and PINK methods with your own parameters:
            - Input your experimental/calculated parameters:
                - Bulk modulus
                - Shear modulus
                - Grüneisen parameter (optional)
            - Compare results between KappaP and PINK methods
            - Process multiple structures (up to 5 files)
            - Explore parameter sensitivity
            
            Perfect for researchers who:
            - Have their own measured/calculated parameters
            - Want to compare different calculation approaches
            - Need to process multiple structures efficiently
            """
        )

    # ---- TECHNICAL DETAILS ----
    with st.container():
        st.write("---")
        st.header("Technical Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Calculated Properties")
            st.write(
                """
                - Basic structural properties
                    - Number of atoms
                    - Density
                    - Volume
                    - Total atomic mass
                - Mechanical properties
                    - Transverse sound velocity
                    - Longitude sound velocity
                    - Speed of sound
                    - Poisson ratio
                - Thermal properties
                    - Acoustic Debye temperature
                    - Grüneisen parameter
                    - Lattice thermal conductivity
                    
                """
            )
            
        with col2:
            st.subheader("Supported File Formats")
            st.write(
                """
                - CIF (Crystallographic Information File)
                - Requirements:
                    - Valid crystal structure
                    - Complete atomic positions
                    - Proper space group information
                - Validation checks included
                """
            )

    # ---- SOFTWARE CERTIFICATE ----
    with st.container():
        st.write("---")
        st.header("Software Certificate")
        # Define path to the certificate PDF
        cert_path = os.path.join(project_root, "image", "R20250315-软件证书.pdf")
        
        # Check if the certificate file exists
        if os.path.exists(cert_path):
            try:
                # Open the PDF file
                doc = fitz.open(cert_path)
                # Select the first page
                page = doc.load_page(0)
                # Render page to an image (pixmap)
                pix = page.get_pixmap()
                doc.close()
                
                # Convert pixmap to bytes for st.image
                img_bytes = pix.tobytes("png")
                
                # Display the image
                st.image(img_bytes, caption='Software Certificate', width=500)

            except Exception as e:
                st.error(f"Error processing PDF file: {e}")
        else:
            # Show a warning if the file is not found
            st.warning(f"Certificate file not found at: {cert_path}")

    # ---- CONTACT INFO ----
    with st.container():
        st.write("---")
        st.header("Contact Information")
        
        contact_info = """
        <p style='font-size: 18px;'>
        For questions, suggestions, or collaboration opportunities:<br><br>
        
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
        <p style='font-size: 18px;'>
        We strive to provide clear documentation and examples to help users effectively utilize our lattice thermal conductivity calculation tools. 
        While we are happy to address issues in the documentation and examples, please note that extensive user support 
        and training are primarily available to our collaborators.
        </p>
        """
        st.markdown(declaration, unsafe_allow_html=True)
