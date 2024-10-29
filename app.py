#!/user/bin/env python3
# -*- coding: utf-8 -*-
import os
import streamlit as st
from multipage import MultiPage
from Pages import KappaP, home, AI4Kappa

st.set_page_config(page_title="Lattice Thermal Conductivity APP", page_icon=":evergreen_tree:", layout="wide")
st.title('Lattice Thermal Conductivity APP')

app = MultiPage()

# add applications
app.add_page('Home', home.app)
app.add_page("KappaP", KappaP.app)
app.add_page("AI4Kappa", AI4Kappa.app)

# Run application
if __name__ == '__main__':
    app.run()