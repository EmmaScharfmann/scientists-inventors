import pandas as pd
import os
import numpy as np

from sentence_transformers import SentenceTransformer, LoggingHandler
import logging
import tqdm as notebook_tqdm
import time
from tqdm import tqdm 


main_path = '/home/fs01/spec1142/Emma/GateKeepers/Text_encoding/'


def encoding():

    """
    This function encodes the titles and abstracts of works using a pre-trained sentence transformer model and saves the embeddings to a TSV file.

    Note:
    - The function assumes that the `main_path` variable is defined elsewhere in the code.
    - The function reads 32 TSV files (named "new_works_texts_0.tsv" to "new_works_texts_31.tsv") containing work data, filters out rows with null titles or abstracts, and encodes the titles and abstracts using a pre-trained sentence transformer model.
    - The function uses a multi-process pool to speed up the encoding process.
    - The function saves the encoded titles and abstracts to a TSV file (named "new_works_encoded_k.tsv", where k is the file index).
    - The function is intended to be run as a standalone script (using the `if __name__ == '__main__':` construct).
    """

    if __name__ == '__main__':
        
        
        for k in tqdm(range(32)):
        
            df = pd.read_csv(main_path + "new_works_texts_" + str(k) + ".tsv" , delimiter = "\t", index_col = 0 )
    
        
            df = df[(df["title"].notnull()) & (df["abstract"].notnull())]
        
            start = time.time()


            logging.basicConfig(format='%(asctime)s - %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S',
                                level=logging.INFO,
                                handlers=[LoggingHandler()])

            os.environ["TOKENIZERS_PARALLELISM"] = "false"



            #Important, you need to shield your code with if __name__. Otherwise, CUDA runs into issues when spawning new processes.


            #Create a large list of 100k sentences
            sentences = df["abstract"].tolist()

            #Define the model
            model = SentenceTransformer('all-MiniLM-L6-v2'  )

            #Start the multi-process pool on all available CUDA devices
            pool = model.start_multi_process_pool(target_devices = ['cpu' for i in range(1) ])

            #Compute the embeddings using the multi-process pool
            emb = model.encode_multi_process(sentences, pool)
            end = time.time()
            print("end abstract" , end - start)


            df["encoded_abstract"] = [ np.around(emb[j] , decimals = 3) for j in range(len(df)) ]

            print("Embeddings abstract computed. Shape:", emb.shape)
            print(" ")

            ## title
            end = time.time()
            print("start title" , end - start)

            ##Create a large list of 100k sentences
            sentences = df["title"].tolist()


            ##Start the multi-process pool on all available CUDA devices
            pool = model.start_multi_process_pool(target_devices = ['cpu' for i in range(1) ])
            ##Compute the embeddings using the multi-process pool
            emb = model.encode_multi_process(sentences, pool )
            end = time.time()
            print("end title" , end - start)

            df["encoded_title"] = [ np.around(emb[j] , decimals = 3) for j in range(len(df)) ]

            print("Embeddings title computed. Shape:", emb.shape)
            print(" ")
            
            df[["encoded_title","encoded_abstract"]].to_csv(main_path + "new_works_encoded_" + str(k) + ".tsv", sep = "\t")
            print("file saved")




encoding()