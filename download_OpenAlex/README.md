# This folder describes how to download and flatten OpenAlex data and how to create, load and index Postgres tables from OpenAlex flat files. 

* The jupyter notebook "Download_OpenAlex.ipynb" describes how to download, flatten OpenAlex data and how to create, load and index Postgres tables.
    * the first section "Download OpenAlex raw data" provides the bash code to download the raw OpenAlex data. Note that it can also be found on OpenAlex website.
    * the section "OpenAlex institutions" provides the code to flatten the institution data downlaoded from OpenAlex, and to save the flat files. Then, it provides the code to create a postgres table to host the institution data. Finally, it provides the code to load the data into the postgres database, to index the table, and to visualize the data from Postgres.
    * the section "OpenAlex authors" provides a similar code to flatten the authors data, and create, load and index the author table into a postgres database. 
    * the section "OpenAlex works" requires to run the python file "flatten_data_works.py" to flatten the works data and the authors-works data, and save the flat files. Once the python file is done, and the flat files are saved, the section "OpenAlex works" provides a similar code to create, load, index and visualize the works table and the authors-works table into the postgres database.
    * the last sections provides the code to flatten the journal, works journal and authors position into flat files.  

* The python file "flatten_data_works.py" flatten the works from OpenAlex and save the flat files.

* Note that downloading a full OpenAlex snapshot requires a considerable memory (~300GB before loading the data to the database). 
* Note that running this section requires an access to a postgres database. The database username and password are store in the text file "database.txt"
* Note that the data needs to be loaded to the tables before the tables are indexed. Otherwise, it increases the loading time.
