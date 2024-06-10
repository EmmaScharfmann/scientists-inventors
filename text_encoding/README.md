# This folder describes how to encode the paper and patent abstracts and titles with a pre-trained model.

The pre-trained model used to compare the titles and abstracts of papers and patents is "all-MiniLM-L6-v2". More details on the model can be found here: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2. 
Note the user is free to change the pre-trained model used in the code of another model. We used "all-MiniLM-L6-v2" as it was specifically fine-tuned for text similarity.  

This section requires the full data (OpenAlex + PatentsView) to be loaded in a Postgres database (username and password are required to run the code, please see folder download_OpenAlex and download_PatentsView). 

* The notebook "Encoding_papers.ipynb" provides the code to encode the titles and abstracts of OpenAlex papers that are not already encoded.
    * The first section provides the code to query the works that are not already encoded. In other words, the code queries from the postgres database, the paper ids that are in the table "works_OpenAlex" but not in the table "encoded_works_OpenAlex".
    * The second section provides the code to query the abstracts and the titles of the works that are not already encoded.
    * The section "Encode the text" provides the code to encode the titles and the abstracts listed in a tsv file with the pre-trained model "all-MiniLM-L6-v2".
    * The section "Load encoding to the database" provides the code to create a Postgres SQL table to store the encoded titles and abstracts. The embeddings are stored as strings. It also provides the code to load the data into the table, and index the table.
    * The last section provides the code to load the data into Google Cloud and to retrieve data stored in Google Cloud.

* Similarly, the notebook "Encoding_patents.ipynb" provides the code to encode the titles and abstracts of PatentsView patents that are not already encoded.
    * The section "Create table to store patent embeddings" provides the code to create a Postgres SQL table to store the titles and abstracts encoding.
    * The second section provides the code to query the patents that are not already encoded. In other words, the code queries from the postgres database the patent ids that are in the table "patents_PatentsView" but not in the table "encoded_patents_PatentsView".
    * The third section provides the code to query the abstracts and the titles of the patents that are not already encoded.
    * The section "Load embeddings into the database" provides the code to load the data into the table, and index the table. The embeddings are stored as strings.

* The python file "encoding.py" provides the code to encode the titles and abstracts stored in a tsv file with a given pre-trained model (here "all-MiniLM-L6-v2"). The encodings are then stored in a flat file.

* The python file "get_texts.py" provides the code to retrieve the titles and abstracts from the database corresponding to the works not yet encoded. 
      
* Note that running this section requires access to a postgres database. The database username and password are stored in the text file "database.txt"
* Note that the data needs to be loaded onto the tables before the tables are indexed. Otherwise, it increases the loading time.
