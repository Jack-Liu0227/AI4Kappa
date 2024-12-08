# Lattice Thermal Conductivity Calculator

This application provides comprehensive tools for calculating and predicting lattice thermal conductivity using both traditional physical models and a new interpretable formula.

The application can calculate the lattice thermal conductivity ($\kappa_L$) of materials through uploading CIF files, offering multiple calculation methods:

- **KappaP**: Based on the Slack model
- **PINK (Physics Informed Kappa)**: An interpretable formula published in [Materials Today Physics](https://doi.org/10.1016/j.mtphys.2024.101549)
- **Custom Calculator**: Combine both methods with user-defined parameters

* The APP has been deployed in Streamlit platform by our team. If you want use this APP, you can access to [https://kappap-ai.streamlit.app/](https://kappap-ai.streamlit.app/).
* You can also deploy the APP on your own computer and server under the guidance of Installation.

The following paper describes the details of the APP.

## Table of Contents

- [Lattice Thermal Conductivity Calculator](#lattice-thermal-conductivity-calculator)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
  - [Run\_APP](#run_app)
  - [Authors](#authors)
  - [License](#license)

## Features

- Multiple calculation methods:
  - KappaP: Traditional Slack model approach
  - PINK : An physics-informed interpretable formula published in [Materials Today Physics](https://doi.org/10.1016/j.mtphys.2024.101549)
  - Custom Calculator: User-defined parameters (up to 5 files)
- Comprehensive output including:
  - Lattice thermal conductivity
  - Intermediate parameters
  - Crystal structure details
- User-friendly interface
- Batch processing capability
- Detailed parameter analysis

## Installation

1. Download project

```bash
  git clone --depth=1 https://github.com/Jack-Liu0227/AI4Kappa.git
  cd KappaP
```

2. Install prerequisites

Option I: If you are familiar with python
    Use the official pip source or Ali pip source

```bash
  python -m pip install -r requirements.txt 
```

  Temporarily change the source method:

```bash
  python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

 Option II: Use of Anaconda) If you are new to Python
    The easiest way of installing the prerequisites is via [conda](https://conda.io/docs/index.html). After installing [conda](http://conda.pydata.org/), run the following command to create a new [environment](https://conda.io/docs/user-guide/tasks/manage-environments.html) named `ltcp_venv` and install all prerequisites:

```bash
  conda create -n KappaP python=3.9 
```

  This creates a conda environment for running the APP. Before using the APP, activate the environment by:

```bash
  conda activate KappaP  
```

  Install all prerequisites

```bash
  python -m pip install -r requirements.txt
```

## Run_APP

After completing the preparations, cd Slack_APP run the following command to run the app
After you finished using the APP, exit the environment by:

```bash
streamlit run app.py
```

## Authors

This software was primarily written by Yujie Liu (Email:liu_yujie@stu.xjtu.edu.cn) who is supervised by [Prof. Zhibin Gao](https://gr.xjtu.edu.cn/web/zhibin.gao).

## License

KappaP is released under the MIT License.
If you use our software, please cite our article.
For any questions, please contact Prof. Zhibin Gao with email: zhibin.gao@xjtu.edu.cn.
