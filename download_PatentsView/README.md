# The folder describes how to download PatentsView data from PatentsView website, and to create, load and index Postgres tables from PatentsView files. 

This folder provides the code to create all PatentsView tables described in the database schema.

* The notebook "Download_PatentsView.ipynb" describes how to download PatentsView tables, and how to create, load and index Postgres tables.
  
    * the first section provides the code to download, unzip and save PatentsView tables. The links to download the different tables can be found on PatentsView website: https://patentsview.org/download/data-download-tables. 
    * the next section "Load data in the database" provides the code to create tables, load the data into the tables and index the tables. For each flat file downloaded from PatentsView website, a new Postgres table needs to be created. Then, the table needs to be loaded onto the table. Finally, the table needs to be indexed.
    * the section query gives an example of an SQL query, and provides the code to test the newly created tables.
    * the last section provides the code to download Patstat data from Google Cloud. Note that this section requires an access to Postgres data and a Google Cloud key.


* Note that PatentsView ids may change between each update. 
* Note that running this section requires access to a postgres database. The database username and password are stored in the text file "database.txt"
* Note that the data needs to be loaded onto the tables before the tables are indexed. Otherwise, it increases the loading time.

