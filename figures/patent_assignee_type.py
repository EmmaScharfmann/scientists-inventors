## this code query the assignee type of each patent using Patstat assignee classification 

import psycopg2
import pandas as pd

main_path = "/home/fs01/spec1142/Emma/GateKeepers/"

patents = pd.read_csv(main_path + 'download_PatentsView/g_patent.tsv' , usecols = [ 'patent_id', 'patent_date' ] ,delimiter = "\t")

## load database username and password
f = open(main_path + "database.txt", "r")
user , password = f.read().split()


def assignee_GK(i):

    """
    This function retrieves the types of assignees for a given list of patents from a PostgreSQL database and saves the data to a TSV file.

    Parameters:
    i (int): The starting index for the patent ID list.(for parallelization)

    Note:
    - The function assumes that the `patents`, `user`, `password`, and `main_path` variables are defined elsewhere in the code.
    - The function establishes a connection to a PostgreSQL database using the `psycopg2` library and executes a SQL query to fetch the assignee types for each patent in the list.
    - The function filters out assignee types that are blank, "INDIVIDUAL", "UNKNOWN", or None.
    - The function creates a DataFrame containing the patent IDs and their corresponding assignee types and saves it to a TSV file (named "type_assignees_i.tsv", where i is the starting index).
    """

    list_patents = list(patents['patent_id'])


    dic_assignees = {} 
    
    list_index = [ k for k in range(i,len(list_patents),24) ]
    list_patent_ids = []
    list_types = [] 

    #establishing the connection
    conn = psycopg2.connect("user=" + user + " password=" + password)

    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    for k in list_index:
        
        patent_id = list_patents[k]
        types = [] 

        text = """SELECT a.psn_sector 
                      FROM patent_numbers_Patstat AS n
                      JOIN patent_numbers_assignees_Patstat AS p ON p.appln_id = n.appln_id
                      JOIN assignees_PATSTAT AS a ON a.person_id = p.person_id
                      WHERE n.publn_nr = '""" + str(patent_id) + """' AND n.publn_auth = 'US'
                      ;"""

        cursor.execute(text)

        res = cursor.fetchall()



        for line in res:


            if line[0] != '' and line[0] != "INDIVIDUAL" and line[0] != "UNKNOWN" and line[0] != None:

                types.append(line[0])
        
        list_types.append("; ".join(types))
        list_patent_ids.append(patent_id)
                        
    df = pd.DataFrame()
    df['patent_id'] = list_patent_ids
    df['assignee_type'] = list_types
    df.to_csv(main_path + "figures/data/type_assignees_" + str(i) + ".tsv" , sep = "\t" , index = False)
    



import warnings

        
from multiprocessing import Process


if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter("ignore",UserWarning)
        
        processes = [Process(target=assignee_GK, args=(k,)) for k in range(24)]
        
        for process in processes:
            process.start()
            
        for process in processes:
            process.join()




df_types = pd.concat([ pd.read_csv(file , sep = "\t") for file in glob.glob(main_path + "figures/data/type_assignees_*") ] )
df_types.to_csv(main_path + "figures/data/type_assignees.tsv" , sep = "\t", index= False)