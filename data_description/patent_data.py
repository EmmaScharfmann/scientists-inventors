##### This code query and store the relevant data (location, country, dates,...) of each patent of each SI in the SI file. ######

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
    f = open(main_path + "data_description/data/dic_patents.json","r")
    import json
    dic_done = json.load(f)

## if no data are generated, load empty dictionary
except:
    dic_done = {}


## get the SI inventors ids 
list_inventor_ids = list(set(df["inventor_id"].tolist()) - set(list(dic_done.keys())))


## This code query the relevant data corresponding to the SI inventor ids
## Note that this code is parallized. Set i=0 and workers=1 to use it without parallelization. 
workers = 24

def get_data_gatekeepers(i):

     """
    This function fetches patent data associated with inventors from a PostgreSQL database and stores it in a JSON file.

    Parameters:
    i (int): The starting index of the thread when selecting inventor IDs from the global list `list_inventor_ids`. Note that this code is parallized. Set i=0 and workers=1 to use it without parallelization. 

    Returns:
    dic (dict): A dictionary containing the processed patent data. The keys are inventor IDs, and the values are dictionaries where the keys are patent IDs and the values are dictionaries containing patent data.

    Note:
    - The function assumes that the `list_inventor_ids`, `user`, `password`, and `main_path` variables are defined elsewhere in the code.
    - The function writes the dictionary to a JSON file every 5000 records. The file name includes the current value of `i`.
    """

    #establishing the connection
    conn = psycopg2.connect(database="spec1142", user=user , password=password , host="192.168.100.54")

    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    dic = {}
    count = 0

    index_inventors = [ k for k in range(i,len(list_inventor_ids),workers)]
    
    for k in index_inventors:
        
        inventor_id = list_inventor_ids[k]

        ## check if the inventor id was already queried. 
        if inventor_id not in dic:
            
            dic[inventor_id] = {}

            text = """ SELECT p.patent_id , 
                              p.patent_date ,
                              
                              i.gender_code,

                              a.assignee_id , 
                              a.disambig_assignee_organization ,
                              
                              pa.filing_date , 

                              la.longitude , 
                              la.latitude  , 
                              la.disambig_country ,
                              li.disambig_country ,
                              la.state_fips,
                              la.county_fips,

                              cpc.cpc_section

                              

                        FROM inventors_PatentsView AS i
                        LEFT JOIN patents_PatentsView as p ON  i.patent_id  = p.patent_id
                        LEFT JOIN applications_PatentsView as pa ON i.patent_id = pa.patent_id
                        LEFT JOIN assignees_PatentsView AS a ON a.patent_id  =  i.patent_id
                        LEFT JOIN patents_cpcs_patentsview AS cpc ON cpc.patent_id  =  i.patent_id 
                        LEFT JOIN locations_PatentsView AS li ON li.location_id =  i.location_id
                        LEFT JOIN locations_PatentsView AS la ON la.location_id = a.location_id
                        WHERE i.inventor_id = '""" + inventor_id + """' 
                        ;"""


            cursor.execute(text)
            res = cursor.fetchall()

            ## organize the data into a dictionary
            for line in res:

                patent_id = line[0]

                if patent_id not in dic[inventor_id]:
                    dic[inventor_id][patent_id] = {}
                    dic[inventor_id][patent_id]["assignee_type"] = []
                    dic[inventor_id][patent_id]["cpcs_sections"] = []
                    dic[inventor_id][patent_id]["assignees"] = {}


                if line[1] != None:
                    dic[inventor_id][patent_id]["grant_date"] = line[1].strftime('%m-%d-%Y')
                else:
                    line[1] = None


                if line[5] != None:
                    dic[inventor_id][patent_id]["application_date"] = line[5].strftime('%m-%d-%Y')
                else:
                    dic[inventor_id][patent_id]["application_date"] = None


                if line[12] != None and line[12] not in dic[inventor_id][patent_id]["cpcs_sections"]:
                    dic[inventor_id][patent_id]["cpcs_sections"].append(line[12])


                dic[inventor_id][patent_id]["male_flag"] = line[2]

                
                if line[3] != None:
                    assignee_id = line[3]
                    dic[inventor_id][patent_id]["assignees"][assignee_id] = {}

                    if line[4] != None:
                        dic[inventor_id][patent_id]["assignees"][assignee_id]["assignee_name"] = line[4]
                    else:
                        dic[inventor_id][patent_id]["assignees"][assignee_id]["assignee_name"] = None

                    dic[inventor_id][patent_id]["assignees"][assignee_id]["longitude"] = line[6]
                    dic[inventor_id][patent_id]["assignees"][assignee_id]["latitude"] = line[7]
                    dic[inventor_id][patent_id]["assignees"][assignee_id]["state"] = line[10]
                    dic[inventor_id][patent_id]["assignees"][assignee_id]["county"] = line[11]

                    if line[8] != None:
                        dic[inventor_id][patent_id]["assignees"][assignee_id]["country_code"] = line[8]
                    else:
                        dic[inventor_id][patent_id]["assignees"][assignee_id]["country_code"] = None


                if line[9] != None:
                    dic[inventor_id][patent_id]["inventor_country_code"] = line[9]
                else:
                    dic[inventor_id][patent_id]["inventor_country_code"] = None

            count += 1

            ## save the file each 5,000 inventors. 
            if count % 5000 == 0:
                import json      
                json = json.dumps(dic)
                f = open(main_path + "data_description/data/dic_patents_dates_locations_cpcs_" + str(i) + ".json","w")
                f.write(json)
                f.close()

    ## save the final file
    import json      
    json = json.dumps(dic)
    f = open(main_path + "data_description/data/dic_patents_dates_locations_cpcs_" + str(i) + ".json","w")
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
dic_patents_sm = {}

for i in range(workers):
    
    f = open(main_path + "data_description/data/dic_patents_dates_locations_cpcs_" + str(i) + ".json","r")
    import json
    dic = json.load(f)
    
    
    
    dic_patents_sm = { **dic_patents_sm , **dic } 


print(len(dic_patents_sm))

## save the dictionary
import json
json = json.dumps(dic_patents_sm)
f = open(main_path + "data_description/data/dic_patents.json","w")
f.write(json)
f.close()