# This section provides the main statistics and descriptive figures and analysis of the SI dataset

This section requires the full data (OpenAlex + PatentsView) to be loaded into a Postgres database (username and password are required to run the codes, please see folder download_OpenAlex and download_PatentsView) as well as the patent and paper titles and abstracts encoded with a pre-trained model (please see folder text_encoding). It also requires the SI dataset to be generated (please see folder run_SI_dataset). 

* The notebook "Doudna_Sankey.ipynb" provides the code to generate a sankey diagram (as illustrated below) showing the SI / pure inventors / pure scientists with the given name. This notebook provides the code to generate a figure (figures/doudna_sankey_05_all.png, figure S1 of the SM).

* The python file "paper_data.py" provides the code to query metadata on SI papers (papers published, dates, concepts and institutions). The data is stored as a json dictionary in the folder "data".
* The python file "patent_data.py" provides the code to query metadata on SI patents (patents granted, dates, cpcs, inventor's gender, assignees and inventor and assignee geographic location). The data is stored as a json dictionary in the folder "data".
* The python file "patent_assignee_type.py" provides the code to query the types of assignees (according to PATSTAT classification) of SI's patents. The data is stored as a tsv file in the folder "data".

* The notebook "Descriptive_figures_SIs.ipynb" provides the code to generate figures (stored in the folder "figures", corresponding to figures S12 to S18 and S23 and S24 of the SM). Note that the 3 python files need to be run and the corresponding data needs to be stored before running this notebook. 
    * The first section provides the code to load the data and create files storing metadata on the SIs (active_inventors, active_authors, dic_clusters_mag.json, dic_types_institutions_mag.json, dic_concepts_cpcs_mag.json, gatekeepers_years_mag.json).
    * The second section provides the code to generate the figures.

* The notebook "Inventors_and_scientists_location.ipynb" provides the code to generate figures (stored in the folder "figures", corresponding to figures S19 to S22 of the SM). 

* The folder "figures" stores the figures describing the SI dataset. The figures are generated using the three jupyter nobebooks "Doudna_Sankey.ipynb", "Descriptive_figures_SIs.ipynb", "Inventors_and_scientists_location.ipynb".

* The folder "data_data_description" stores the data related to the SIs:
    * metadata on the SI papers (dic_papers and dic_papers_missing) and metadata on the SI patents (dic_patents and dic_patents_missing) generated using "paper_data.py" and "patent_data.py". 
    * data on the SI active years (active_inventors, active_authors), metadata on each SI (dic_clusters_mag.json, dic_types_institutions_mag.json, dic_concepts_cpcs_mag.json, gatekeepers_years_mag.json) generated using "Descriptive_figures_SIs.ipynb". 
    * GDP data (from https://www.bea.gov/data/gdp/gdp-county-metro-and-other-areas) and county shapes (https://public.opendatasoft.com/explore/dataset/us-county-boundaries/table/).
    * OpenAlex institutions (from OpenAlex folder).
* It provides all the data required to generate the figures.

      
* Note that running this section requires access to a postgres database. The database username and password are stored in the text file "database.txt"


Example of SIs / pure scientists / pure inventors named "Doudna" : ![doudna](figures/doudna_sankey_05_all.png)
