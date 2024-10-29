#!/user/bin/env python3
# -*- coding: utf-8 -*-
#!/user/bin/env python3
# -*- coding: utf-8 -*-
import os,glob

import streamlit_scripts.file_op as fo
import streamlit_scripts.chang_model as cm

import streamlit as st
import pandas as pd
import predict


def display_results(df):
    formula=r"$$\Kappa_L=\frac{G V_s V^{\frac{1}{3}}}{N T} \cdot e^{-\gamma}$$"
    template=f"""
            The volume of the crystal structure is {df["Volume (Å3)"].iloc[0]} Å$^3$.<br>
            The Bulk modulus of the crystal structure is {df["Bulk modulus (GPa)"].iloc[0]} GPa.<br>
            The Shear modulus of the crystal structure is {df["Shear modulus (GPa)"].iloc[0]} GPa.<br>
            The sound velocity of the crystal structure is {df["Speed of sound (m s-1)"].iloc[0]} m/s.<br>
            The Grunisen parameter of the crystal structure is {df["Grüneisen parameter"].iloc[0]}.<br>
            The formula of the lattice thermal conductivity is: {formula}.<br>
            The calculated lattice thermal conductivity is {df["Kappa_cal"].iloc[0]} W/(m·K).<br>
            """
    return template

def app():
    st.title("CGCNN")
    sour_path = os.path.abspath('.')
    root_dir="root_dir"
    root_dir_path=os.path.join(sour_path,root_dir)
    uploaded_files = st.sidebar.file_uploader("Please upload the primitive cell CIF not the conventional cell CIF!!!",['cif'],accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            save_path = os.path.join(root_dir_path, file_name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            st.write(f"File saved: {file_name}")

        cif_path_list = glob.glob(os.path.join(root_dir_path, '*.cif'))
        for i in range(len(cif_path_list)):
            cif_file_path = cif_path_list[i]
            if fo.is_valid_cif(cif_file_path):
                pass
            else:
                cif_name = os.path.basename(cif_file_path)
                st.write(f"{cif_name} Invalid CIF file with no structures!")
                os.remove(cif_file_path)
                st.write(f"In order to prevent program errors, invalid CIF file {cif_name} has been deleted.")
        if len(glob.glob(os.path.join(root_dir_path, '*.cif'))):
            cif_path_list,cif_name_list=fo.create_id_prop(root_dir_path)
            first_cif_path=cif_path_list[0]
            cry_content = fo.get_crystalline_content(first_cif_path)
            results_csv_path = os.path.join(sour_path, "test_results.csv")
            try:
                model_path = ''
                cm.copy_model(model_path, sour_path)
                predict.main(root_dir_path)
            except:
                pass
            try:
                test_results = pd.read_csv(results_csv_path, header=None)
                test_results.columns = ["ID", "RAND", "Kappa"]

                if 'Kappa' in test_results.columns:
                    test_results_p = test_results.iloc[:, 2]
                    test_results_p.index = test_results["ID"]
                    st.write("---")
                    st.dataframe(test_results_p)
                    st.write("---")
                    st.write(f"The file name of displaying crystalline is: {test_results_p.index[0]}")
                    st.write("The information of uploaded crystal structure is:")
                    st.write(cry_content, unsafe_allow_html=True)
                    st.write("---")

                    template = 'The calculated lattice thermal conductivity is {:.2f} W/(m·K).<br>'.format(
                        test_results_p[0])
                    st.write(template, unsafe_allow_html=True)
                else:
                    st.write("Column 'Kappa' not found in the results.")
            except Exception as e:
                st.write(e)

            fo.del_cif_file(root_dir_path)

    declaration = """<p style='font-size: 22px;'>We strive to have clear documentation and examples to help everyone with using Al4Kappa on their own. 
        We will happily fix issues in the documentation and examples should you find any, 
        however, we will not be able to offer extensive user support and training, except for our collaborators.</p>"""
    st.write("---")
