# Opticalmaterials Database

Tools for auto-generating battery materials database.

## Installation

### Pre-requisite
This instruction of installation is based on a Windows computer.

The quickest way to install these tools is via Anaconda. 
Anaconda can be downloaded free of charge from the Anaconda official website [https://www.anaconda.com/products]. This installation process also requires the Microsoft Visual Studio C++ 2014 or later version installed. They can be downloaded freely from the Microsoft official website [https://visualstudio.microsoft.com/].

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
    
The Anaconda Prompt should then print as following:

    (chemdataextractor) D:\opticalmaterials_database>python main.py
    parsing ./demo/1.html
    {'RefractiveIndex': {'raw_value': '1.388', 'value': [1.388], 'specifier': 'n', 'compound': {'Compound': {'names': ['n-Heptane', 'n-heptane']}}}, 'metadata': "{'title': 'Influence of excited state aromaticity in the lowest excited singlet states of fulvene derivatives  ', 'authors': ['Martin\\xa0Rosenberg', 'Henrik\\xa0Ottosson', 'Kristine\\xa0Kilså', 'Martin\\xa0Rosenberg', 'Henrik\\xa0Ottosson', 'Kristine\\xa0Kilså'], 'publisher': 'Royal Society of Chemistry', 'journal': 'Physical Chemistry Chemical Physics', 'date': '2011/07/06', 'language': 'en', 'volume': '13', 'issue': '28', 'firstpage': '12912', 'lastpage': '12919', 'doi': '10.1039/C0CP02821E', 'pdf_url': 'https://pubs.rsc.org/en/content/articlepdf/2011/cp/c0cp02821e', 'html_url': 'https://pubs.rsc.org/en/content/articlelanding/2011/cp/c0cp02821e'}"}
    ...
    ...
    parsing ./demo/4.html
    {'RefractiveIndex': {'raw_value': '1.470', 'value': [1.47], 'specifier': 'refractive index', 'compound': {'Compound': {'names': ['trimethylolpropane triacrylate']}}, 'raw_sentence': 'Then , the templates were infiltrated with viscous mixtures of commercialized ethoxylated ( 15 ) trimethylolpropane triacrylate ( EO15TMPTA , refractive index 1.470 ) and polyethylene glycol ( 600 ) diacrylate ( PEG600DA , refractive index 1.468 ) ( Fig. S1 ) with various weight ratios from 1 : 2 to 1 : 6 .'}, 'metadata': "{'title': 'Reconfigurable photonic crystals with optical bistability enabled by “cold” programming and thermo-recoverable shape memory polymers  ', 'authors': ['Wenbin\\xa0Niu', 'Lingcheng\\xa0Qu', 'Rongwen\\xa0Lyv', 'Shufen\\xa0Zhang', 'Wenbin\\xa0Niu', 'Lingcheng\\xa0Qu', 'Rongwen\\xa0Lyv', 'Shufen\\xa0Zhang'], 'publisher': 'Royal Society of Chemistry', 'journal': 'RSC Advances', 'date': '2017/04/24', 'language': 'en', 'volume': '7', 'issue': '36', 'firstpage': '22461', 'lastpage': '22467', 'doi': '10.1039/C6RA28682H', 'pdf_url': 'https://pubs.rsc.org/en/content/articlepdf/2017/ra/c6ra28682h', 'html_url': 'https://pubs.rsc.org/en/content/articlelanding/2017/ra/c6ra28682h'}"}
    {'RefractiveIndex': {'raw_value': '1.468', 'value': [1.468], 'specifier': 'refractive index', 'compound': {'Compound': {'names': ['diacrylate']}}, 'raw_sentence': 'Then , the templates were infiltrated with viscous mixtures of commercialized ethoxylated ( 15 ) trimethylolpropane triacrylate ( EO15TMPTA , refractive index 1.470 ) and polyethylene glycol ( 600 ) diacrylate ( PEG600DA , refractive index 1.468 ) ( Fig. S1 ) with various weight ratios from 1 : 2 to 1 : 6 .'}, 'metadata': "{'title': 'Reconfigurable photonic crystals with optical bistability enabled by “cold” programming and thermo-recoverable shape memory polymers  ', 'authors': ['Wenbin\\xa0Niu', 'Lingcheng\\xa0Qu', 'Rongwen\\xa0Lyv', 'Shufen\\xa0Zhang', 'Wenbin\\xa0Niu', 'Lingcheng\\xa0Qu', 'Rongwen\\xa0Lyv', 'Shufen\\xa0Zhang'], 'publisher': 'Royal Society of Chemistry', 'journal': 'RSC Advances', 'date': '2017/04/24', 'language': 'en', 'volume': '7', 'issue': '36', 'firstpage': '22461', 'lastpage': '22467', 'doi': '10.1039/C6RA28682H', 'pdf_url': 'https://pubs.rsc.org/en/content/articlepdf/2017/ra/c6ra28682h', 'html_url': 'https://pubs.rsc.org/en/content/articlelanding/2017/ra/c6ra28682h'}"}
    68 relations in total
    ./demo/4.html is done
    
After the raw data is extracted, they are stored in a json file under ```./save```. The raw data also needs to be cleaned and converted into a standard format. We provide the data cleaning code in ```data_clean.ipynb```. The users are also freely to use any other way they want to filter, clean, and process the data.

## Citation

