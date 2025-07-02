#!/user/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Zhibin Gao's Group. All rights reserved.
# Author: Zhibin Gao
# Email: zhibin.gao@xjtu.edu.cn
import streamlit as st
class MultiPage:
    """Framework for combining multiple streamlit applications"""
    def __init__(self) -> None:
        self.pages = []

    def add_page(self, title, func):
        """Add a new page to the app
        
        Args:
            title: The title of page
            func: The function to call for this page
        """
        self.pages.append(
            {
                'title': title,
                'function': func
            }
        )

    def run(self):
        """Run the selected page"""
        page = st.sidebar.selectbox(
            'app navigation',
            self.pages,
            format_func=lambda page: page['title']  # Function to modify the display of the labels.
        )
        page['function']()