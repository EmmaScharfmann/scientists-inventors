# This folder describes how to create the novelty measure. 

The novelty measure used in our project corresponds to a score between -1 and 1 which represents the opposite of the similarity between the paper (or patent) abstracts and the abstracts of the papers (or patents) published (or granted) the 5 years before their publication (or grant) year. For each paper (resp patent), we calculate the cosine similarity between the embedded paper abstract (resp patent) and the embedded abstracts of all papers published (resp patents granted). Then, we take the average cosine similarity, which gives a score between -1 and 1. 
The highest this score is, the more similar the paper (or patent) is to prior literature and the less novel it is. Therefore, we define the novelty score as the opposite of the average cosine similarity between the abstract and the abstracts published in the 5 previous years. 

Distribution of the paper average similarity scores: ![paper novelty](paper_novelty.jpg)
Distribution of the patent average similarity scores: ![patent novelty](patent_novelty.jpg)

* The jupyter notebook "novelty_measure.ipynb" provides the code to generate the novelty measure based on the papers and patents hosted in the postgres database.
    * The first section provides the code to generate the patent novelty and the second section provides the code to generate the paper novelty
    * In each section, the first subsection "Generate embedded abstracts files by year" provides the code to organize the embedded abstracts into flat files. The paper or patent abstract embeddings are first extracted from the postgres database, then cleaned and organized by publication (or grant) year into flat files.
    * In each section, the second subsection "Calculate novelty" provides the code to generate the novelty scores. The papers (or patents) from a given year are loaded (current knowledge), as well as the papers (or patents) published in the 5 previous years (prior work). Then, the average of the embedded abstracts of the previous works is computed and the dot product between the current knowledge and the average prior work is taken. It gives the opposite of the novelty measure.

*  The data files are saved in the folder "data".
*  The figures "paper_novelty.jpg" and "patent_novelty.jpg" illustrate the distribution of the novelty scores. 

* Note that running this section requires access to a postgres database. The database username and password are stored in the text file "database.txt"
* Note that taking the average of the embedding and then the dot product is equivalent to taking the dot products and then the average of the dot products by linearity. 