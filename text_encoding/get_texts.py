import pandas as pd
from tqdm import tqdm
import psycopg2
from mpi4py import MPI



f = open('/home/fs01/spec1142/Emma/GateKeepers/' + "database.txt", "r")
user , password = f.read().split()


main_path = '/home/fs01/spec1142/Emma/GateKeepers/Text_encoding/'



f = open(main_path + "papers_to_encode.json","r")
import json
dic_works = json.load(f)


list_works = list(dic_works.keys())


def get_text(i):

        """
    This function retrieves the titles and abstracts of works from a PostgreSQL database and saves them to a TSV file.

    Parameters:
    i (int): The starting index for selecting works.

    Note:
    - The function assumes that the `list_works`, `main_path`, `user`, `password`, and `host` variables are defined elsewhere in the code.
    - The function establishes a connection to a PostgreSQL database using the `psycopg2` library and executes a SQL query to fetch the titles and abstracts of works based on their IDs.
    - The function stores the retrieved titles and abstracts in a dictionary and then converts the dictionary to a DataFrame.
    - The function saves the DataFrame to a TSV file (named "new_works_texts_i.tsv", where i is the starting index).
    - The function closes the database connection after fetching the data.
    """
    


    #establishing the connection
    conn = psycopg2.connect(database="spec1142", user=user , password=password , host="192.168.100.54")

    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    
    list_index = [ k for k in range(i,len(list_works),32)] 

    dic_works_texts = {}

    for k in list_index:
        
        work_id = list_works[k]
        
        #Creating table as per requirement
        sql ="""SELECT work_id , title , abstract
                FROM   works_OpenAlex 
                WHERE work_id = '""" + work_id + """'
                ;"""

        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result) > 0:
            dic_works_texts[work_id] = {}
            dic_works_texts[work_id]["title"] = result[0][1]
            dic_works_texts[work_id]["abstract"] = result[0][2]

    #Closing the connection
    conn.close()
        
    
    table = pd.DataFrame(dic_works_texts).T
    table.to_csv(main_path + "new_works_texts_" + str(i) + ".tsv", sep = "\t")



    
    
import warnings

        
from multiprocessing import Process


if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter("ignore",UserWarning)
        
        processes = [Process(target=get_text, args=(k,)) for k in range(32)]
        
        for process in processes:
            process.start()
            
        for process in processes:
            process.join()


    
    
