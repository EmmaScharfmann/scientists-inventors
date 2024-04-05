# Scientist-Inventor dataset

This reposistory provides the code to link worldwide scientists to US inventors. This code what used to create the scientist-inventor database, publicly available at XXX: xxxxxxxx.com. 
You can refer to our paper "paper title" for more details: paper link. 
This github provides the code to generate the statistics, tables and figures describe in the paper. 

* The folders "download OpenAlex" and "download PatentsView" provide the code to download the worldwide science publication database OpenAlex and the US patent database PatentsView.
* The folder "text_encoding" provides the code to encode the paper's and patent's titles and abstracts with the open source pre-trained model "all-MiniLM-L6-v2".
* The folder "train_the_model" provides the code to train predictive model used to identify papers and patents written by the same individual. It also provdes the code to create the training set, compare different classification models, and create figures SX to SX. 
* The folder "run_SI_dataset" provides to code to link the full worldwide scientists database to the US inventors database. 
* The folder "validation" provides the code used to validate the SI dataset against GoogleScholar and against the patent to paper citations. The manual and automated files generated to validate the SI dataset against GoogleScholar can be downloaded in this folder, as well as the code to generate figure SX.
* The folder "novelty_measure" provides the code to generate our novelty measure. The distribution of the paper and patent novelty measure can be found in this folder.
* The folder "figures" provides the code to generate the descriptive figures and statitstics about the SI dataset. It provides the code to query all relevant information on SI's papers and patents (dates, institutions, geographic data, field, cpcs, type of affiliations...), the figures SX to SX, as well as figure 1.
* The folder "regressions" provides the code to generate the files used in the regressions, as well as the do files to run the regressions and the regression's results.

Note that (almost) all the codes require a username and password to query a postgres database (created based on the code provided in the folders "download_OpenAlex" and "download_PatentsView"). The schema of the postgres database used in the provided codes is described in the [database_schema](database_schema.png).

Below the database schema: 

![database_schema](database_schema.png)



