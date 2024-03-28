## Packages 

import json, requests 
import pandas as pd
import time 
import csv
import gzip
import subprocess
from tqdm import tqdm 
import numpy as np
from mpi4py import MPI


main_path = '/home/fs01/spec1142/'
data = 'openalex-snapshot/data'
path = '/home/fs01/spec1142/Emma/Download_OpenAlex/'


## reconstruct the abstract from the inverted index

def reconstruction_abstract(abstract_inverted_index):
    # return the abstract is the abstract exists in the database, else, return None
    
    if abstract_inverted_index != '' and abstract_inverted_index != None and abstract_inverted_index != {} and abstract_inverted_index["InvertedIndex"] != {}:
        size = abstract_inverted_index["IndexLength"]
        text = np.full_like(np.empty((size)), '', dtype = 'object')
        for k,values in abstract_inverted_index["InvertedIndex"].items():
            for v in values:
                text[v] = k
        
        return ' '.join(text)
    else:
        # return none if there is no abtract
        return None


## list_folders : list of the folders in the folder "data/institutions/", which represents the institution files



cmd = 'ls ' + main_path + data + '/works'
list_folders_works = subprocess.check_output(cmd,  shell=True)
list_folders_works = list_folders_works.decode().split("\n")
list_folders_works.remove('')
list_folders_works = list_folders_works[1:]




def upload_authors(i):

    """
    This function processes gzipped JSON files containing work data, extracts relevant information, and stores it in intermediate TSV files.

    Parameters:
    i (int): The starting index for selecting files (for parallelization)

    Returns:
    None. The function directly writes the processed data to TSV files.

    Note:
    - The function assumes that the `list_folders_works`, `main_path`, `data`, and `path` variables are defined elsewhere in the code.
    - The function iterates over a list of folders, and for each folder, it gets a list of files and selects files based on the starting index `i`.
    - For each file, the function unzips it, creates two dictionaries (`dic_works` and `dic_authors_works`), and fills them with the extracted data.
    - The function then converts these dictionaries to DataFrames and writes them to TSV files. The TSV files are named based on the folder name and the starting index `i`.
    - The function appends to the TSV files if they already exist, except for the first file, where it overwrites the file.
    - The function also prints the time taken to process all the files.
    """
    

    start = time.time()

    ## search in each folder

    for folder in list_folders_works:

        print("folder: " , folder)

        ##get the files in the folder

        cmd = 'ls ' + main_path + data + '/works/' + folder
        files = subprocess.check_output(cmd,  shell=True)
        files = files.decode().split("\n")
        files.remove('')
        print("Files: " , files) 


        index_files = [ k for k in range(i,len(files),32) ] 
        
        

        ##search in each file in the folder 
        for k in index_files:
            
            file = files[k]

            ##unzip file
            with gzip.open(main_path + data +"/works/" + folder + "/" + file, 'rb') as f:

                #create dictionary 
                dic_works = {}
                dic_authors_works = {}
                count = 0 


                print("File:" , file)

                #open file 

                #fill out the intermediate dictionary 
                for line in f:

                    line = json.loads(line)

                    work_id = line["id"][22:]


                    dic_works[work_id] = {}
                    if line["doi"] != None:
                        dic_works[work_id]["doi"] = line["doi"][16:]
                    else:
                        dic_works[work_id]["doi"] = None
                    if "pmid" in line["ids"] and line["ids"]["pmid"] != None:
                        dic_works[work_id]["pmid"] = line["ids"]["pmid"][32:]
                    else:
                        dic_works[work_id]["pmid"] = None

                    dic_works[work_id]["title"] = line["title"]
                    dic_works[work_id]["abstract"] = reconstruction_abstract(line["abstract_inverted_index"])

                    dic_works[work_id]["publication_date"] = line["publication_date"]
                    dic_works[work_id]["type"] = line["type"]


                    # host_venue / publisher and sources 
                    if "host_venue" in line:
                        if "id" in line["host_venue"] and line["host_venue"]["id"] != None:
                            dic_works[work_id]["venue_or_source"] = line["host_venue"]["id"][22:]
                        else:
                            dic_works[work_id]["venue_or_source"] = None
                        dic_works[work_id]["publisher_id"] = None
                    elif "primary_location" in line and line["primary_location"] != None:
                        if "id" in line["primary_location"] and line["primary_location"]["id"] != None:
                            dic_works[work_id]["venue_or_source"] = line["primary_location"]["id"][22:]
                        else:
                            dic_works[work_id]["venue_or_source"] = None

                        if "publisher_id" in line["primary_location"] and line["primary_location"]["publisher_id"] != None:
                            dic_works[work_id]["publisher_id"] = line["primary_location"]["publisher_id"][22:]
                        else:
                            dic_works[work_id]["publisher_id"] = None


                    else:
                        dic_works[work_id]["venue_or_source"] = None
                        dic_works[work_id]["publisher_id"] = None

                    if "language" in line:
                        dic_works[work_id]["language"] = line["language"]







                    dic_works[work_id]["first_page"] = line["biblio"]["first_page"]
                    dic_works[work_id]["last_page"] = line["biblio"]["last_page"]
                    dic_works[work_id]["volume"] = line["biblio"]["volume"]
                    dic_works[work_id]["issue"] = line["biblio"]["issue"]

                    dic_works[work_id]["cited_by_count"] = line["cited_by_count"]
                    dic_works[work_id]["concepts"] = "; ".join([ elem["display_name"] for elem in line["concepts"] if "display_name" in elem])
                    dic_works[work_id]["referenced_works"] = "; ".join([ elem[22:] for elem in line["referenced_works"]])
                    dic_works[work_id]["last_update"] = line["updated"][:10]


                    authorships = line["authorships"]
                    for elem in authorships:
                        if "id" in elem["author"] and elem["author"]["id"] != None:
                            if len(elem["institutions"]) > 0:
                                for institution in elem["institutions"]:
                                    dic_authors_works[count] = {}
                                    dic_authors_works[count]["work_id"] = work_id
                                    dic_authors_works[count]["author_id"] = elem["author"]["id"][22:]
                                    if "id" in institution and institution["id"] != None:
                                        dic_authors_works[count]["institution_id"] = institution["id"][22:]
                                        dic_authors_works[count]["institution_name"] = None
                                    else:
                                        dic_authors_works[count]["institution_id"] = None
                                        dic_authors_works[count]["institution_name"] = institution["display_name"]

                                    count += 1

                            else:
                                dic_authors_works[count] = {}
                                dic_authors_works[count]["work_id"] = work_id
                                dic_authors_works[count]["author_id"] = elem["author"]["id"][22:]
                                dic_authors_works[count]["institution_id"] = None
                                dic_authors_works[count]["institution_name"] = None

                                count += 1
                            


                if k == index_files[0]:

                    table = pd.DataFrame(dic_works).T
                    table.to_csv(path + "OA_works_intermediate/" + folder + "_" +  str(i) +  ".tsv", sep = "\t", index_label = "work_id" , mode='w')
                    table = pd.DataFrame(dic_authors_works).T
                    table.to_csv(path + "OA_authors_works_intermediate/" + folder + "_" +  str(i) +  ".tsv", sep = "\t", index = False, mode = 'w')

                else:
                    table = pd.DataFrame(dic_works).T
                    table.to_csv(path + "OA_works_intermediate/" + folder + "_" +  str(i) +  ".tsv", sep = "\t", index_label = "work_id" , mode='a', header = False)
                    table = pd.DataFrame(dic_authors_works).T
                    table.to_csv(path + "OA_authors_works_intermediate/" + folder + "_" +  str(i) + ".tsv", sep = "\t", index = False, mode = 'a', header = False)



    end = time.time()
    print("Time:" , end - start) 





#upload_authors(MPI.COMM_WORLD.Get_rank())
       
            
import warnings

        
from multiprocessing import Process


if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter("ignore",UserWarning)
        
        processes = [Process(target=upload_authors, args=(k,)) for k in range(32)]
        
        for process in processes:
            process.start()
            
        for process in processes:
            process.join()
       

            




