# Opticalmaterials Database

Tools for auto-generating battery materials database.

## Installation

### Pre-requisite
This instruction of installation is based on a Windows computer.

The quickest way to install the ChemDataExtractor version is via Anaconda. 
Anaconda can be downloaded free of charge via the Anaconda official website [https://www.anaconda.com/products]. This installation process also requires the Microsoft Visual Studio C++ 2014 or later version installed. They can be downloaded freely via the Microsoft official website [https://visualstudio.microsoft.com/].

### Create a new visual environment via Conda

Open the build-in command line tool **Anaconda Prompt** of Anaconda through the start manu, then create a new visual environment named chemdataextractor with Python version 3.7:

    conda create -n chemdataextractor python=3.7
    
Then, activate this visual environment:
    
    conda activate chemdataextractor
    
    
### Download the bespoke version of ChemDataExtractor from this repository

Simply click the green **Code** button on the repository website and click **Download Zip** to download the repository files to your local computer. Then unzip the zipped file to a desired directory. In this example, we unzip the zipped file to D: and the directory of the unziped folder then becomes ```D:\opticalmaterials_database\```

### Install ChemDataExtractor and relavent files

Enter our destination folder by type the following command in the Anaconda Prompt:

    cd D:\opticalmaterials_database\
    
Now, the Anaconda Prompt should looks like this:

    (chemdataextractor) D:\opticalmaterials_database>|
    
Install the dependency packages:
    
    pip install -r requirements.txt
     
Next, install the original version of ChemDataExtractor:

    conda config --add channels conda-forge
    conda install chemdataextractor
    
Before next step, copy and paste the **chemdataextractor folder** and the **tabledataextractor folder** to the site-package folder of your visual environment. That is:

    Copy and paste D:\opticalmaterials_database>chemdataextractor(folder) and D:\opticalmaterials_database>tabledataextractor(folder) to
    
    Your_Anaconda_installation_directory\Anaconda\envs\chemdataextractor\Lib\site-packages\
    
This step is to use the bespoke version of ChemDataExtractor for this study to overwrite the original version of ChemDataExtractor. Note that the last step, installation of the original version of ChemDataExtractor, is still necessary because it is the pre-requisite of the next step. 

In order to function, ChemDataExtractor requires a variety of data files, such as machine learning models, dictionaries, and word clusters. Get these by running:

    cde data download
    
This will download all the necessary data files to the data directory. 

Now, the software tools used for this study has been fully installed.


## Usage

To extract raw data from text, you need to provide the root of the paper folder, output root to data record folder, start and end index of papers, and the file name to be saved within the ```main.py```.

For example, extract the example papers within ```D:\opticalmaterials_database\demo\``` by typing the following command in the same Anacomda Prompt:

    python main.py 
    
After the raw data is extracted, it needs to be cleaned and converted into a standard format. We provide the data cleaning code in dataclean.ipynb. The final data format can be .json, .csv or .db.


Markdown 目录：
[TOC]

Markdown 标题：
# 这是 H1
## 这是 H2
### 这是 H3

Markdown 列表：
- 列表项目
1. 列表项目

*斜体*或_斜体_
**粗体**
***加粗斜体***
~~删除线~~

Markdown 插入链接：
[链接文字](链接网址 "标题")

Markdown 插入图片：
![alt text](/path/to/img.jpg "Title")

Markdown 插入代码块：
    ```python
    #!/usr/bin/python3
    print("Hello, World!");
    ```

Markdown 引用：
> 引用内容

Markdown 分割线：
---

Markdown 换行：
<br>

Markdown 段首缩进：
&ensp; or &#8194; 表示一个半角的空格
&emsp; or &#8195;  表示一个全角的空格
&emsp;&emsp; 两个全角的空格（用的比较多）
