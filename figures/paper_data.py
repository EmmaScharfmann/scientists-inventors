##### This code query and store the relevant data (location, country, dates,...) of each paper of each SI in the SI file. ######

## load packages 
import pandas as pd 
import psycopg2
import json, requests

main_path = "/home/fs01/spec1142/Emma/GateKeepers/"

## load database username and password
f = open(main_path + "database.txt", "r")
user , password = f.read().split()


## load the SI file 
df = pd.read_csv(main_path + "gatekeepers_intermediate_clean_v5.tsv", sep = "\t" )

    
## load dictionary with the inventor data already generated 
try:
    f = open(main_path + "figures/data/dic_papers.json","r")
    import json
    dic_done = json.load(f)

## if no data are generated, load empty dictionary
except:
    dic_done = {}


## get the SI authors ids 
list_authors_ids = list(set(df["author_id"].tolist()) - set(list(dic_done.keys())))


## get the main concepts (level 0) from OpenAlex
#create a URl, that will be used for OpenAlex
def URL(base_URL , entity_type , filters):
    url = base_URL + entity_type + filters 
    return url

#from an internet link, extract the data and load the data in the jyputer notebook 
def get_data(url):
    url = requests.get(url)
    text = url.text
    import json
    data = json.loads(text)
    return data


list_concepts = []
base_URL_OA = f'https://api.openalex.org/'
filter_works = f'concepts?filter='
filter_by_date = "level:0&page=" + str(1) + "&sort=works_count:desc&per-page=" + str(200) + "&mailto=emma_scharfmann@berkeley.edu" 
url = URL(base_URL_OA , filter_works, filter_by_date)
data = get_data(url)["results"]
for k in range(len(data)):
    list_concepts.append(data[k]["display_name"] )
    
    
set_concepts = set(list_concepts)

## This code query the relevant data corresponding to the SI author ids
## Note that this code is parallized. Set i=0 and workers=1 to use it without parallelization. 
workers = 24
def get_data_gatekeepers(i):

     """
    This function fetches papers data associated with authors from a PostgreSQL database and stores it in a JSON file.

    Parameters:
    i (int): The starting index of the thread when selecting author IDs from the global list `list_author_ids`. Note that this code is parallized. Set i=0 and workers=1 to use it without parallelization. 

    Returns:
    dic (dict): A dictionary containing the processed paper data. The keys are author IDs, and the values are dictionaries where the keys are paper IDs and the values are dictionaries containing paper data.

    Note:
    - The function assumes that the `list_author_ids`, `user`, `password`, and `main_path` variables are defined elsewhere in the code.
    - The function writes the dictionary to a JSON file every 5000 records. The file name includes the current value of `i`.
    """
    
    dic = {}
    
    #establishing the connection
    conn = psycopg2.connect(database="spec1142", user=user , password=password , host="192.168.100.54")

    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    count = 0
    

    for k in range(0 + i , len(list_author_ids)  , workers):
        
        author_id = list_author_ids[k]
        
        ## check if the author id was already queried. 
        if author_id not in dic:

            dic[author_id] = {}
            
            text = """ SELECT w.work_id , w.publication_date, w.concepts  , string_agg(wa.institution_id , ';')
                        FROM authors_OpenAlex AS a
                        JOIN works_authors_OpenAlex as wa ON a.author_id = wa.author_id
                        JOIN works_OpenAlex AS w ON wa.work_id  = w.work_id
                        WHERE a.author_id = '""" + author_id + """' 
                        GROUP BY w.work_id , w.publication_date, w.concepts 
                        ;"""

            cursor.execute(text)
            res = cursor.fetchall()
            
            ## organize the data into a dictionary
            for line in res:
                if line[0] != None:
                    work_id = line[0]
                    dic[author_id][work_id] = {}

                    if line[1] != None:
                        dic[author_id][work_id]["publication_date"] = line[1].strftime('%m-%d-%Y')
                    else:
                        dic[author_id][work_id]["publication_date"] = None

                    if line[2] != None:
                        dic[author_id][work_id]["concepts"] = list(set(line[2].split("; ")) & set_concepts)
                    else:
                        dic[author_id][work_id]["concepts"] = None

                    if line[3] != None:
                        dic[author_id][work_id]["institution_id"]  =  list(set(line[3].split(';')))
                    else:
                        dic[author_id][work_id]["institution_id"] = None



            count += 1

            ## save the file each 5,000 authors. 
            if count % 5000 == 0:
                import json
                json = json.dumps(dic)
                f = open(main_path + "figures/data/dic_dates_institutions_concepts_" + str(i) + ".json","w")
                f.write(json)
                f.close()

    ## save final file
    import json
    json = json.dumps(dic)
    f = open(main_path + "figures/data/dic_dates_institutions_concepts_" + str(i) + ".json","w")
    f.write(json)
    f.close()
    
    
    conn.close()

    
        


## parallelization of the code. Set workers=1 to use it without parallelization. 
import warnings     
from multiprocessing import Process

if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter("ignore",UserWarning)
        
        processes = [Process(target=get_data_gatekeepers, args=(k,)) for k in range(workers)]
        
        for process in processes:
            process.start()
            
        for process in processes:
            process.join()



## concatenate the intermediate files 
dic_papers_sm = {}

for i in range(workers):
    
    f = open(main_path + "figures/data/dic_dates_institutions_concepts_" + str(i) + ".json","r")
    import json
    dic = json.load(f)
    
    
    
    dic_papers_sm = { **dic_papers_sm , **dic } 


print(len(dic_papers_sm))

## save the dictionary
import json
json = json.dumps(dic_papers_sm)
f = open(main_path + "figures/data/dic_papers.json","w")
f.write(json)
f.close()
