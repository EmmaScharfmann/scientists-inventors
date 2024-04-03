####################################### Packages to import ####################################################################

##import packages 

import pandas as pd
from math import radians, cos, sin, asin, sqrt
import random 
import numpy as np
import json, requests 
import geopy.distance
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns
import unicodedata
from metaphone import doublemetaphone
from fuzzywuzzy import fuzz
from difflib import SequenceMatcher
import re
import pickle5 as pickle
from tqdm import tqdm
import psycopg2
import spacy
from nltk.corpus import stopwords 
from nltk.stem import PorterStemmer
import glob 

from mpi4py import MPI

import warnings
warnings.filterwarnings('ignore')

#!python -m spacy download en_core_web_lg
spacy_nlp = spacy.load("en_core_web_lg")



####################################### Files to import or to modify #########################################################





##main path of the data
main_path  = '/home/fs01/spec1142/Emma/GateKeepers/'


f = open(main_path + "database.txt", "r")
user , password = f.read().split()



##name cleaning - elements to remove or merge from the names 
name_del = ["2nd", "3rd", "jr", "jr.", "junior", "sr", "sr.", "senior", "i", 'ii' , 'iii']

ln_suff= ["oster", "nordre", "vaster", "aust", "vesle", "da", "van t", "af", "al", "setya", "zu", "la", "na", "mic", "ofver", "el", "vetle", "van het", "dos", "ui", "vest", "ab", "vste", "nord", "van der", "bin", "ibn", "war", "fitz", "alam", "di", "erch", "fetch", "nga", "ka", "soder", "lille", "upp", "ua", "te", "ni", "bint", "von und zu", "vast", "vestre", "over", "syd", "mac", "nin", "nic", "putri", "bet", "verch", "norr", "bath", "della", "van", "ben", "du", "stor", "das", "neder", "abu", "degli", "vre", "ait", "ny", "opp", "pour", "kil", "der", "oz",  "von", "at", "nedre", "van den", "setia", "ap", "gil", "myljom", "van de", "stre", "dele", "mck", "de", "mellom", "mhic", "binti", "ath", "binte", "snder", "sre", "ned", "ter", "bar", "le", "mala", "ost", "syndre", "sr", "bat", "sndre", "austre", "putra", "putera", "av", "lu", "vetch", "ver", "puteri", "mc", "tre", "st"]


## load dictionary with the distribution of the last names: 
f = open(main_path + "frequency_last_names.json","r")
import json
dic_last_names = json.load(f)

## load dictionary with the distribution of the first names: 
f = open(main_path + "frequency_first_names.json","r")
import json
dic_first_names = json.load(f)



## load dictionary with the missing institutions (key: display name, values: city, country, longitude, latitude) 
dic_missing_ids = {}


## load dictionary with the missing institutions (key: display name, values: city, country, longitude, latitude) 
institutions = pd.read_csv(main_path + "figures/data/institutions_up_to_20230817.tsv" , delimiter = "\t", index_col = 0 )
dic_institutions = institutions.to_dict("index")

# extract all the cities from the OpenAlex institutions, as well as their locations (longitude latitude) 

#flatten the institution dictionary
for institution in list(dic_institutions.keys()):
    dic_institutions[institution]["region"] = dic_institutions[institution]["region"]
    dic_institutions[institution]["city"] = dic_institutions[institution]["city"]
    dic_institutions[institution]["longitude"] = dic_institutions[institution]["longitude"]
    dic_institutions[institution]["latitude"] = dic_institutions[institution]["latitude"]
    dic_institutions[institution]["country"] = dic_institutions[institution]["country"]
    

#store the longitude / latitude cooresponding to the cities
dic_cities = {}

for institution in list(dic_institutions.keys()):
    if dic_institutions[institution]["city"] not in dic_cities and dic_institutions[institution]["latitude"] != None:
        dic_cities[dic_institutions[institution]["city"]] = []
    if dic_institutions[institution]["city"] in dic_cities and [ dic_institutions[institution]["latitude"] , dic_institutions[institution]["longitude"] ] not in dic_cities[dic_institutions[institution]["city"]]:
        dic_cities[dic_institutions[institution]["city"]].append([ dic_institutions[institution]["latitude"] , dic_institutions[institution]["longitude"] ])
    
        

#get the list of the cities and of the countries from OpenAlex institution table
table = pd.DataFrame(dic_institutions).T    

list_cities = set(table["city"].tolist())
list_countries = set(table["country"].tolist())
list_country_codes = set(table["country_code"].tolist())


ps = PorterStemmer()  

stop_words = set(stopwords.words('english')) | set(stopwords.words('german'))  | set(stopwords.words('spanish')) | set(stopwords.words('french')) 

set_institutions_words = {"univers" , "colleg" , "hospit" , "institut" , "research", "medicin" , "medic" , "center" , "state" , "scienc" , "servic" , "health", "foundat" , "corpor" , "school", "depart"}

words = stop_words | set_institutions_words



 



########################################### Fonctions to load  ###############################################################


#merge the particles/suffixes/prefixes with the last name 
#ln_suff file can be modified if more or less suffixes want to be merged 
def ln_suff_merge(string):
    for suff in ln_suff:
        if f"{' ' + suff + ' '}" in string or string.startswith(f"{suff + ' '}"):
            string =  string.replace(f"{suff + ' '}", suff.replace(" ",""))
    return string


#suppress all the unwanted suffixes from a string
#name_del file can be modified if more or less suffixes want to be suppressed 
def name_delete(string):
    for suff in name_del:
        if f"{' ' + suff + ' '}" in string or string.endswith(f"{' ' + suff}"):
            string =  string.replace(f"{suff}","")
    return string


#normalize a string dat that represents often a name. 
def normalize(data):
    normal = unicodedata.normalize('NFKD', data).encode('ASCII', 'ignore')
    val = normal.decode("utf-8")
    # delete unwanted elmt
    val = name_delete(val)
    # lower full name in upper
    val = re.sub(r"[A-Z]{3,}", lambda x: x.group().lower(), val)
    # add space in front of upper case
    if "Mac" not in val and "Mc" not in val:
        val = re.sub(r"(\w)([A-Z])", r"\1 \2", val)
    # Lower case
    val = val.lower()
    # remove special characters
    val = re.sub('[^A-Za-z0-9 -]+', ' ', val)
    # remove multiple spaces
    val = re.sub(' +', ' ', val)
    # remove trailing spaces
    val = val.strip()
    # suffix merge
    val = ln_suff_merge(val)

    return val


#normalize a string dat that represents an institution. 
def normalize_inst(data):

    # Lower case
    data = data.lower()
    # remove special characters
    data = re.sub('[^A-Za-z0-9 ]+', ' ', data)
    
    return data


#return a ratio of similarity of letters between two strings (to handle in the first names errors)
def match_ratio(string1,string2):
    return fuzz.ratio(string1, string2)


#return 4 if string1 and string2 are the same
#return 3 if string1 and string2 sound the same
#otherwise, return less
def metaphone(string1,string2):
    if string1==string2:
        return 4
    tuple1 = doublemetaphone(string1)
    tuple2 = doublemetaphone(string2)
    if tuple1[0] == tuple2[0]:
        return 3
    elif tuple1[0] == tuple2[1] or tuple1[1] == tuple2[0]:
        return 2
    elif tuple1[1] == tuple2[1]:
        return 1
    else:
        return 0
    
    
#compare name1 and name2. Return 1 if name1 and name2 might represent the same individual, otherwise 0.
def comparison(name1 , name2):
    
    if name1 == name2:
        return 1
    
    #if there is no first name, retrun it's a match
    if name1 == "" or name2 == "":
        return 1
    
    #if some first names exist:
    list_name1 = name1.split()
    list_name2 = name2.split()
    
    #minimum number of first names to match
    number_match = min( len(list_name1) , len(list_name2))
    
    #for each name, check if there is a match
    count_match = 0
    for elem1 in list_name1:
        match = 0
        
        #if we just have the initial:
        if len(elem1) == 1:
            for elem2 in list_name2:
                if elem1[0] == elem2[0]:
                    match = 1
        else:
            for elem2 in list_name2:
                #if we just have the initial:
                if len(elem2) == 1 and elem1[0] == elem2[0]:
                    match = 1
                    
                #if elem1 and elem2 are entire first names that sound the same and have a ratio of common letters higher thsan 85%, it's a match
                elif len(elem2) > 1 and (metaphone(elem1,elem2) > 2 or match_ratio(elem1 , elem2) > 85 ) :
                    match = 1
                    
        #count the number of first names that match    
        count_match += match
        
    #check if we have enough first names that match 
    if count_match < number_match:
        return 0
    else:
        return 1

    
## count the number of in common authors
def number_of_in_common_authors(paper , patent ):
    
    authors = paper["co_authors"]

    inventors = patent["co_inventors"]
    
    #count the number of names in common, and store the names in common
    count = 0
    list_in_common_authors = []
    
    for name_inventor in inventors:
        
        for name_author in authors:
            
            if name_inventor == name_author:
                count += 1 
                list_in_common_authors.append(name_author + "-" + name_inventor)
                
            
            elif len(set(name_inventor.split()) & set( name_author.split())) > 0:
                 
                match = comparison(name_author , name_inventor)

                #if the first names match, we store the first names that are matching and their index 
                if match == 1:
                    count += 1 
                    list_in_common_authors.append(name_author + "-" + name_inventor)
                    


    #return 1) the number of names in common, 2) the list of names in common, 3) their index 
    return  count ,  list_in_common_authors 


#quantify the similarity between two names 
def score(author , inventor , name):
    
    score = 0
    
    #get the distribution of the last names (from the dictionary dic_last_names)
    #it's possible to change the distribution of the last names by changing the dictionary
    name = normalize(name)
    if name in dic_last_names:
        dist = dic_last_names[name]
    else:
        dist = 0        
   
    #remove the last name from the author name

    author_names = " ".join([ elem[0] + " " + elem[1] if len(elem)==2 else elem for elem in author.split() ]).split()

    if name in author_names:
        author_names.remove(name)
    
    inventor_names = inventor.split()

    if name in inventor_names:
        inventor_names.remove(name)

    
    #sorte the cleaned author name by the lenght of the first names if there is the initial of the middle name
    if len(inventor_names) > 1 and len(inventor_names[1]) > 1 and len(inventor_names[0]) < 3:
        inventor_names = sorted(inventor_names, key=len, reverse=True)
    if len(author_names) > 1 and len(author_names[1]) > 1 and len(author_names[0]) <3 :
        author_names = sorted(author_names , key=len , reverse=True)
    
  
    #if there is not first name, the socre is 0.4
    if author_names == [] or inventor_names == []:
        score = 0.4


    #if both author and inventor have an entire first name (not just initial)
    elif len(author_names[0]) > 2 and len(inventor_names[0]) > 2:
        
        #if the first names match:
        if author_names[0] == inventor_names[0]:
            
            #we add the first name distribution to the distribution of the full name
            if author_names[0] in dic_first_names:
                dist_first_name = dic_first_names[author_names[0]]
            else:
                dist_first_name = 0
                
            #if a middle name match, the score is 1     
            if len(author_names) > 1 and len(inventor_names) > 1 and author_names[1][0] == inventor_names[1][0]:
                dist = dist*dist_first_name
                score = 1
            
            #if there is no middle name, the score is 0.8
            else:
                dist = dist*dist_first_name
                score = 0.8
                
        #if the first names don't match:
        else:
            
            #if the first names sound the same and have more than 85% of letters in common, the score is 0.7
            if (metaphone(author_names[0],inventor_names[0])) > 2 or match_ratio(author_names[0],inventor_names[0]) > 85 :
                
                #we add the first name distribution to the distribution of the full name
                if inventor_names[0] in dic_first_names:
                    dist_first_name = dic_first_names[inventor_names[0]]
                else:
                    dist_first_name = 0
                dist = dist*dist_first_name
                score = 0.7
                    
            #else, the score is 0.1
            else:
                score = 0.1
    
    #if the author or the inventor only have an initial:
    
    elif len(author_names[0]) < 3 or len(inventor_names[0]) < 3:

        inventor_names = inventor.split()
        #if only the first initial of the author matches with the first initial of the inventor, the score is 0.6

        if author_names[0][0] == inventor_names[0][0]:
            score = 0.6
            
            
            #if more than one initial are matching, the score is 0.8
            if len(author_names) > 1 and len(inventor_names) > 1 and author_names[1][0] == inventor_names[1][0]:
                score = 0.8
        #if only a middle initial matches with am initial, the score is 0.2
        else:
            score = 0.2
    
    #return the similarity between the inventor and author name, the distribution of the matching name, 
    #the author and inventor names and the similarity between the inventor and author name normalize by the distribution of the name. 
    return   score, dist,  author  , inventor , score /(1 + dist)
    
        
    
## calculate efficiently the dot product between two vectors
def norm(vector):
    return sqrt(sum(x * x for x in vector))    

def cosine_similarity2(vec_a, vec_b):
        norm_a = norm(vec_a)
        norm_b = norm(vec_b)
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        return dot / (norm_a * norm_b)
     
       
## tranform string into vector
def clean_encoding(encoded_text):
    if encoded_text == None:
        return None
    else:
        if "\n" in encoded_text:
            encoded_text = encoded_text.replace("\n" , "")
        encoded_text = encoded_text[1:-1]
        encoded_text = list(map(float , encoded_text.split()))
        return encoded_text
    
    
## quantify similarity between the titles (with BERT) 
def similarity_title(paper , patent):
    
    #return the similarity between the titles if exist, else return none
    if patent["encoded_title"] == None or paper["encoded_title"] == None or patent["encoded_title"] == [] or paper["encoded_title"] == []:
        return None
    
    else:
        return cosine_similarity2(patent["encoded_title"], paper["encoded_title"])

    
## quantify similarity between the abstract (with BERT) 
def similarity_abstract(paper , patent):
    
    #return the similarity between the abstracts if exist, else return none
    if patent["encoded_abstract"] == None or paper["encoded_abstract"] == None or patent["encoded_abstract"] == [] or paper["encoded_abstract"] == []:
        return None
    
    else:
        return cosine_similarity2(patent["encoded_abstract"], paper["encoded_abstract"])

    

#get the location from an institution mame
def get_location_display_name(display_name):
    #clean the institution name
    display_name = ''.join([i for i in display_name if not i.isdigit()])
    display_name = display_name.replace("*" , "")
    display_name = display_name.replace("#TAB#" , "")
    display_name = display_name.replace("  " , " ")
    
    #extract the location and organisation from the institution name
    doc = spacy_nlp(display_name.strip())
    location_entities= set()
    organization_entities = set()
    for i in doc.ents:
        entry = str(i.lemma_).lower()
        display_name = display_name.replace(str(i).lower(), "")
        if i.label_ in ["GPE", "GEO","LOC"]:
            location_entities.add(i)
        if i.label_ in ["ORG"]:
            organization_entities.add(i)
            
    #return         
    return location_entities , organization_entities


#get the coordinates from an institution name
def get_location_missing( display_name):
    
    # extract all the cities from the OpenAlex institutions, as well as their locations (longitude latitude) 

    #get the location from an institution name
    dic = {}
    location = get_location_display_name(display_name)[0]
    cities = set()
    countries = set()
                    
                    
    #search a cooresponding city in OpenAlex institution's cities                
    for elem in location:
        elem = str(elem).title()
                    
        if elem in list_cities and elem in dic_cities:
            cities.add(elem)

        if elem in list_countries or elem in list_country_codes:
            countries.add(elem)
                
    dic["city"] = list(cities - countries)
    dic["country"] = list(countries)
    
    #get the coordinates associated with a city
    if cities != set():
        dic["longitude"] = float(dic_cities[list(cities)[0]][0][1])
        dic["latitude"] = float(dic_cities[list(cities)[0]][0][0])
        
    #return a dictionary where the key is the institution names and the values are the city, country, longitude, latitude
    return dic



## calculate efficiently the geographic distance between two points on the earth
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    km = 6371* c
    return km



##calculate the minimal distance between the paper and the patent assignee
def distance_assignees(paper , patent , data_author):
     
    #create the list of coordinates corresponding to the paper and the patent assignee
    coords_patents = list(set([ (long, lat) for long,lat in zip(patent["assignee_longitude"], patent["assignee_latitude"]) ]))
    coords_papers = list(set([ (long, lat) for long,lat in zip(paper["longitude"], paper["latitude"]) ]))

    #if there is no coordinates corresponding to the paper, take the last institution of the author
    if coords_papers == []:
        coords_papers = list(set([ (long, lat) for long,lat in zip(data_author["longitude"], data_author["latitude"]) ]))

    if coords_patents == [] or coords_papers ==[]:
        return None
    
    
    #calculate the minimal distance
    else: 
        distance = np.inf
        for coord_patent in coords_patents:
            
            if coord_patent in coords_papers:
                return 0
            
            else:
                for coord_paper in coords_papers:
                    if coord_patent[0] != None and coord_patent[1] != None and coord_paper[0] != None and coord_paper[1] != None:
                        dist = haversine(coord_patent[0], coord_patent[1], coord_paper[0], coord_paper[1])
                        if dist < distance:
                            distance = dist


    if distance == np.inf:
        return None
    
    #return the minimal distance
    return distance




##calculate the minimal distance between the paper and the patent inventors
def distance_inventors(paper , patent , data_author):
    
    #create the list of coordinates corresponding to the paper and the patent inventors
    coords_patents = [(patent["inventor_longitude"], patent["inventor_latitude"])]
    coords_papers = list(set([ (long, lat) for long,lat in zip(paper["longitude"], paper["latitude"]) ]))

    #if there is no coordinates corresponding to the paper, take the last institution of the author
    if  coords_papers == []:
        coords_papers = list(set([ (long, lat) for long,lat in zip(data_author["longitude"], data_author["latitude"]) ]))

    if coords_patents == [] or coords_papers ==[]:
        return None
    
    #calculate the minimal distance
    else: 
        distance = np.inf
        for coord_patent in coords_patents:
            
            if coord_patent in coords_papers:
                return None
            
            else:
                for coord_paper in coords_papers:
                    if coord_patent[0] != None and coord_patent[1] != None and coord_paper[0] != None and coord_paper[1] != None:
                        dist = haversine(coord_patent[0], coord_patent[1], coord_paper[0], coord_paper[1])
                        if dist < distance:
                            distance = dist

    if distance == np.inf:
        return None
        
    #return the minimal distance
    return distance




#clean institution string
def clean_institution_name(institution):
    
    institution = set(normalize_inst(institution).split())
    set_institution = set([ps.stem(word) for word in institution if word not in words ])

    return set_institution


#count the number of words in common between the cleaned patent and the paper's institutions
def similarity_institution_name(paper, patent , data_author):
    
    assignee = patent["assignee_organization"]
    if assignee == None:
        return 0
    
    else:
        assignee = clean_institution_name(assignee)
        
    institution = paper["institution_name"]
    if institution == None:
        institution = data_author["last_known_institution_display_name"]
        
    if institution == None:
        return 0
    
    else:
        institution = clean_institution_name(institution)
        
    return len(institution & assignee)
    
        
        
        
#get number of in common citing or cited patents 
def in_common_citing_papers(paper , patent ):
    #return the number of papers that are cited by the selected patent and by selected paper 
    
    referenced_paper = paper["referenced_works"]
    cited_papers = patent["cited_papers"]
    
    if referenced_paper == None or cited_papers == None:
        return 0
 
    else:
        return len( cited_papers & referenced_paper ) 
    


from scipy.stats import chi2
#calculate the likelihood of the patent in the papers dates distributions
def calculate_likelihood_chi2(dic_dates, patent):
    patent_date = patent["patent_date"].year
    df, loc, scale = dic_dates["chi_dist"] 
    res = chi2.logpdf(patent_date, df, loc, scale)
    if res < -5000:
        res = -5000
    return res



def comparison_pairs2(dic_comparison , paper , patent , data_author , dic_dates):
    
    #dictionary that regroup all the comparison feathures between a paper and a patent
    #key: paper number + space + patent number

    dic_comparison["number_in_common_authors"] , dic_comparison["list_in_common_authors"]   = number_of_in_common_authors(paper , patent)

    dic_comparison["distance_assignees"] = distance_assignees(paper , patent , data_author)
    dic_comparison["distance_inventors"] = distance_inventors(paper , patent , data_author)

    dic_comparison["in_common_citing_papers"] = in_common_citing_papers(paper , patent )

    #dic_comparison["in_common_citing_or_cited_patents"] = in_common_citing_or_cited_patents(paper , patent )
    #dic_comparison["similarity_cpcs_wipos_concepts"] = similarity_cpcs_wipos_concepts(paper , patent)

    dic_comparison["similarity_institution"] = similarity_institution_name(paper , patent , data_author)

    if dic_dates != None: 
        dic_comparison["date_likelihood"] = calculate_likelihood_chi2(dic_dates, patent)
   
        dic_comparison["date_difference"] = abs(patent["patent_date"].year - dic_dates["mean_dates"])
        dic_comparison["publications_range"] = dic_dates["max_dates"] - dic_dates["min_dates"]
        dic_comparison["number_publications"] = len(dic_dates["list_dates"])
    else:
        dic_comparison["date_likelihood"] = None
        dic_comparison["date_difference"] = None
        dic_comparison["publications_range"] = None
        dic_comparison["number_publications"] = None


    return dic_comparison



    
####################################### Function to create the gatekeepers file ##############################################

    
    
    
#from a last name, gives the PatentsView ids, patent numbers and first names that correspond to the given last name.

def get_PatentsView_inventors_ids(last_name):
    
    #query the ids, patent numbers, first names that correspond to the last name.
    

    #establishing the connection
    conn = psycopg2.connect(database="spec1142", user=user , password=password , host="192.168.100.54")

    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    last_name = last_name.lower()
    
    text = """SELECT   i.inventor_id , 
                       i.disambig_inventor_name_first , 
                       i.disambig_inventor_name_last 

              FROM inventors_PatentsView as i

              WHERE f_unaccent(i.disambig_inventor_name_last) ILIKE '% """ + last_name + """ %'
              
              OR f_unaccent(i.disambig_inventor_name_last) ILIKE '""" + last_name + """ %'

              OR f_unaccent(i.disambig_inventor_name_last) ILIKE '""" + last_name + """'
              
              OR f_unaccent(i.disambig_inventor_name_last) ILIKE '% """ + last_name + """'
              
              ;"""

    cursor.execute(text)

    res = cursor.fetchall()


    #Closing the connection
    conn.close()

    
    dic_inventors = {}
    for line in res:

        inventor_id = line[0]
        
        if "'" in inventor_id:
            inventor_id = inventor_id.replace( "'" , "''")
            
        dic_inventors[inventor_id] = {}
        inventor_first_name = line[1]
        if inventor_first_name == None:
            inventor_first_name = ''

        dic_inventors[inventor_id]["inventor_first_name"] = normalize(inventor_first_name)
        dic_inventors[inventor_id]["inventor_last_name"] = normalize(line[2])


    dic_inventor_first_names = {}
    for inventor_id in list(dic_inventors.keys()):
        first_names = dic_inventors[inventor_id]["inventor_first_name"].split()

        for first_name in first_names:

            if first_name != '' and first_name not in dic_inventor_first_names:
                dic_inventor_first_names[first_name] = []
            dic_inventor_first_names[first_name].append(inventor_id)
                             

    #return a list of ids, first names that correspond to the given last name
    return dic_inventors , dic_inventor_first_names









#from a last name, gives the PatentsView ids, patent numbers and first names that correspond to the given last name.

def get_OpenAlex_author_ids(last_name , first_name):
    
    #query the ids, patent numbers, first names that correspond to the last name.
    
    #establishing the connection
    conn = psycopg2.connect(database="spec1142", user=user , password=password , host="192.168.100.54")

    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    if first_name == '':
        
        
        text = """SELECT   a.author_id ,
                       a.display_name , 
                       a.orcid , 
                       a.last_known_institution_id , 
                       a.last_known_institution_display_name
                       
          
          FROM authors_OpenAlex AS a
                    
          WHERE f_unaccent(a.display_name) ILIKE '""" + last_name + """ %'
          
          OR f_unaccent(a.display_name) ILIKE ' """ + last_name + """%'

          OR f_unaccent(a.display_name) ILIKE '% """ + last_name + """ %';"""
        
    
    else:


        first_name = first_name.lower()
        last_name = last_name.lower()
    
        text = """SELECT   a.author_id ,
                           a.display_name , 
                           a.orcid , 
                           a.last_known_institution_id , 
                           a.last_known_institution_display_name
                           

              FROM authors_OpenAlex AS a

              WHERE ( f_unaccent(a.display_name) ILIKE '""" + last_name + """ %'
          
              OR f_unaccent(a.display_name) ILIKE '% """ + last_name + """'
    
              OR f_unaccent(a.display_name) ILIKE '% """ + last_name + """ %') 

              AND ( f_unaccent(a.display_name) ILIKE '""" + first_name + """ %'

                    OR f_unaccent(a.display_name) ILIKE '% """ + first_name + """'

                    OR f_unaccent(a.display_name) ILIKE '% """ + first_name + """ %'

                    OR f_unaccent(a.display_name) ILIKE '""" + first_name[0] + """ %'

                    OR f_unaccent(a.display_name) ILIKE '""" + first_name[0] + """.%'
                    
                    );"""

        
    cursor.execute(text)
    res = cursor.fetchall()


    #Closing the connection
    conn.close()


    dic_author = {}
    for line in res:

        author_id = line[0]
        dic_author[author_id] = {}
        dic_author[author_id]["author_name"] = normalize(line[1])
        dic_author[author_id]["orcid"] = line[2]
        dic_author[author_id]["last_known_institution_id"] = line[3]
        dic_author[author_id]["last_known_institution_display_name"] = line[4]
        
        if line[3] in dic_institutions:
            data = dic_institutions[line[3]]
            dic_author[author_id]["longitude"] = [data["longitude"]]
            dic_author[author_id]["latitude"] = [data["latitude"]]
        else:
            dic_author[author_id]["longitude"] = []
            dic_author[author_id]["latitude"] = []
            


    #return a list of ids, first names that correspond to the given last name
    return dic_author








#Display a matrix with the inventor names and author names. 
#For the author and inventor names that might represent the same person, the score is greater than 0

def get_pd_table_comparison(last_name):
    
    ## dic_comparison just to get the DataFrame
    dic_comparison = {}
    
    ##store the ids of the match
    dic_ids = {}
    
    ## query the authors and the inventors corresponding to the last name
    
    dic_inventors, dic_inventor_first_names = get_PatentsView_inventors_ids(last_name)
    
        
    dic_authors_full  = {}

    
    for first_name in list(dic_inventor_first_names.keys()):

                
        dic_authors = get_OpenAlex_author_ids(last_name , first_name)        
        
        dic_authors_full = { **dic_authors_full , **dic_authors }
    
        ## normalize last name
        last_name_norm = normalize(last_name)

        count = 0

        ##for each author id, 
        
        #start = time.time()
        
        for author_id in dic_authors:
            

            ## extract the first names of the author
            name_norm = dic_authors[author_id]["author_name"]
            first_names = normalize(name_norm.replace(last_name_norm , ""))

            ## separate the first name initials
            if name_norm.split()[0] == last_name_norm and len(first_names) < 4:
                first_names = normalize(first_names.replace("" , " "))

            ## get the first names
            dic_authors[author_id]["author_first_names"] = first_names

            ## get the author name
            name = dic_authors[author_id]["author_first_names"]  + " " + last_name_norm
            
            if name not in dic_comparison:
                dic_comparison[name] = {}

            first_names_OA = dic_authors[author_id]["author_first_names"]
            

            ## compare the author name with the inventor's name
            for inventor_id in dic_inventor_first_names[first_name]:

                first_names_PV = dic_inventors[inventor_id]["inventor_first_name"]
                last_names_PV = dic_inventors[inventor_id]["inventor_last_name"]


                #compare the OA first names and the PV first names. 
                # add the similarity score into dic_comparison: the first key is the author name, the second key is the inventor name. 
                if comparison(first_names_OA , first_names_PV) == 1:
                    res =  score(name, first_names_PV + " " + last_name_norm , last_name_norm)
                    

                    inventor_author_pair = name + "%" + first_names_PV + " " + last_names_PV
                    
                    ## store the normalize simiarity score
                    dic_comparison[name][first_names_PV + " " + last_names_PV] = res[-1]
                        
                    
                    if res[-1]**2 + 1 > 1.25:
                        
                                                
                        if inventor_author_pair not in dic_ids:

                            dic_ids[inventor_author_pair] = {}
                            dic_ids[inventor_author_pair]["OpenAlex_id"] = set()
                            dic_ids[inventor_author_pair]["PatentsView_id"] = set()
                            dic_ids[inventor_author_pair]["Raw_score"] = res[0]
                            dic_ids[inventor_author_pair]["Norm_score"] = res[-1]

                        if author_id not in dic_ids[inventor_author_pair]["OpenAlex_id"]:
                            dic_ids[inventor_author_pair]["OpenAlex_id"].add(author_id)

                        if inventor_id not in dic_ids[inventor_author_pair]["PatentsView_id"]:
                            dic_ids[inventor_author_pair]["PatentsView_id"].add(inventor_id)
                            


                else:
                    dic_comparison[name][first_names_PV + " " + last_names_PV] = 0
        #end = time.time()
        #print(end - start)



    #return 1) table a DataFrame with the inventor and author names and their similarity scores
    #return 2) dic_comparison a dictionary with the author name (first key) and inventor name (second key) and their similarity scores (values) 
    #returm 3) and 4) the list of patents_ids and the list of author ids updated
    return dic_comparison , dic_ids , dic_authors_full , dic_inventors
        




    
#get the patents associated with the patent numbers stored in the dictionary dic_ids

def get_patents(dic_ids):
    
    dic_patents = {}
    
    #establishing the connection
    conn = psycopg2.connect(database="spec1142", user=user , password=password , host="192.168.100.54")

    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    
    for names in dic_ids:
        inventor_name = names.split("%")[1]
        set_inventor_ids = dic_ids[names]["PatentsView_id"]
        for inventor_id in set_inventor_ids:           
                
            if inventor_id not in dic_patents:
        
                dic_patents[inventor_id] = {}
                
                text = """SELECT i.patent_id, 
                                 i.disambig_inventor_name_first ,
                                 i.disambig_inventor_name_last ,
                                 li.longitude,
                                 li.latitude,
                                 p.patent_date,
                                 pe.encoded_title , 
                                 pe.encoded_abstract , 
                                 string_agg(a.disambig_assignee_organization, '%')  , 
                                 string_agg( CAST(la.longitude AS VARCHAR), ','),
                                 string_agg(CAST(la.latitude AS VARCHAR), ','),
                                 string_agg( CONCAT(co.disambig_inventor_name_first , ' ' ,  co.disambig_inventor_name_last) , ','  ) ,
                                 string_agg(npc.work_id , ',')
                                 
           
                          FROM inventors_PatentsView AS i
                          LEFT JOIN patents_PatentsView AS p ON  i.patent_id  = p.patent_id
                          LEFT JOIN locations_PatentsView AS li ON  i.location_id  = li.location_id
                          LEFT JOIN assignees_PatentsView AS a ON  i.patent_id = a.patent_id
                          LEFT JOIN locations_PatentsView AS la ON a.location_id = la.location_id
                          LEFT JOIN inventors_PatentsView AS co ON i.patent_id = co.patent_id
                          LEFT JOIN non_patent_citations_matt_marx AS npc ON CONCAT('us-' , i.patent_id) = npc.patent_id
                          LEFT JOIN encoded_patents_patentsview AS pe ON  i.patent_id = pe.patent_id
                          
                          WHERE i.inventor_id = '""" + inventor_id + """'

                          GROUP BY i.patent_id,
                                 i.disambig_inventor_name_first ,
                                 i.disambig_inventor_name_last ,
                                 li.longitude,
                                 li.latitude,
                                 p.patent_date,
                                 pe.encoded_title , 
                                 pe.encoded_abstract"""

                cursor.execute(text)
                res = cursor.fetchall()
                
                for line in res:
                    
                    
                    patent_id = line[0]
                    dic_patents[inventor_id][patent_id] = {}
                    dic_patents[inventor_id][patent_id]["inventor_id"] = inventor_id
                    dic_patents[inventor_id][patent_id]["inventor_first_name"] = line[1]
                    dic_patents[inventor_id][patent_id]["inventor_last_name"] = line[2]
                    dic_patents[inventor_id][patent_id]["inventor_longitude"] = line[3]
                    dic_patents[inventor_id][patent_id]["inventor_latitude"] = line[4]
                    dic_patents[inventor_id][patent_id]["patent_date"] = line[5]
                    
                    try:
                        dic_patents[inventor_id][patent_id]["encoded_title"] = clean_encoding(line[6])
                        dic_patents[inventor_id][patent_id]["encoded_abstract"] = clean_encoding(line[7])
                    except:
                        dic_patents[inventor_id][patent_id]["encoded_title"] = None
                        dic_patents[inventor_id][patent_id]["encoded_abstract"] = None
                
                        
                        
                    if line[8] != None:
                        dic_patents[inventor_id][patent_id]["assignee_organization"] = "; ".join(list(set(line[8].split("%"))))
                    else:
                        dic_patents[inventor_id][patent_id]["assignee_organization"] = line[8]
                    if line[9] != None:
                        dic_patents[inventor_id][patent_id]["assignee_longitude"] = list(set([ float(elem) for elem in line[9].split(",")]))
                        dic_patents[inventor_id][patent_id]["assignee_latitude"] = list(set([ float(elem) for elem in line[10].split(",")]))
                    else:
                        dic_patents[inventor_id][patent_id]["assignee_longitude"] = []
                        dic_patents[inventor_id][patent_id]["assignee_latitude"] = []
                        
                    dic_patents[inventor_id][patent_id]["co_inventors"] = [ normalize(elem) for elem in set(line[11].split(",")) ] 
                    if line[12] != None:
                        dic_patents[inventor_id][patent_id]["cited_papers"] = set(line[12].split(","))
                    else:
                        dic_patents[inventor_id][patent_id]["cited_papers"]  = None
                        
                        
                    dic_patents[inventor_id][patent_id]["inventor_name"]  = inventor_name
                    
                    
    
    #Closing the connection
    conn.close()
    
    return dic_patents





def save_time(dic_ids ):
    
    dic_patents = get_patents(dic_ids)
    
    dic_good_ids = {}
    dic_encoding = {}
    
    dic_comparison = {}
    dic_papers = {}
    
    #establishing the connection
    conn = psycopg2.connect(database="spec1142", user=user , password=password , host="192.168.100.54")

    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    for name in dic_ids:
     
        
        OpenAlex_ids = dic_ids[name]['OpenAlex_id']
        PatentsView_id = dic_ids[name]['PatentsView_id']
                                
            
        for author_id in OpenAlex_ids:

            if author_id not in dic_encoding:
                
                dic_comparison[author_id] = {}
                dic_papers[author_id] = {}
                dic_encoding[author_id] = {}
                

                text = """ SELECT we.work_id,  we.encoded_title , we.encoded_abstract , string_agg(wa.institution_id , ',') , string_agg(wa.institution_name, ',')
                            FROM works_authors_OpenAlex AS wa
                            LEFT JOIN encoded_works_openalex AS we ON wa.work_id = we.work_id
                            WHERE wa.author_id = '"""+ str(author_id) +"""'
                            GROUP BY we.work_id,  we.encoded_title , we.encoded_abstract
                            ;"""
                
                cursor.execute(text)
                res = cursor.fetchall()
                
                for line in res:
                    work_id = line[0]
                    
                    
                    if work_id != None and work_id not in dic_encoding[author_id]:
                        dic_papers[author_id][work_id] = {}
                        
                        
                        dic_papers[author_id][work_id]["institution_name"] = line[4]
                        
                        dic_papers[author_id][work_id]["longitude"] = []
                        dic_papers[author_id][work_id]["latitude"] = []
                        
                        if line[3] != None:
                            institution_ids = line[3].split(",")
                            for institution_id in institution_ids:
                                if institution_id in dic_institutions:
                                    data = dic_institutions[institution_id]
                                    dic_papers[author_id][work_id]["longitude"] += [data["longitude"]]
                                    dic_papers[author_id][work_id]["latitude"] += [data["latitude"]]
                                    dic_papers[author_id][work_id]["institution_name"] = data["display_name"]



                        institution_name = dic_papers[author_id][work_id]["institution_name"]
                        if dic_papers[author_id][work_id]["longitude"] == [] and institution_name != None and institution_name != "":
                            if institution_name in dic_missing_ids and "longitude" in dic_missing_ids[institution_name]:
                                dic_papers[author_id][work_id]["longitude"] += [dic_missing_ids[institution_name]["longitude"]]
                                dic_papers[author_id][work_id]["latitude"] += [dic_missing_ids[institution_name]["latitude"]]

                            else:
                                dic = get_location_missing( institution_name )
                                dic_missing_ids[institution_name] = dic
                                if "longitude" in dic:
                                    dic_papers[author_id][work_id]["longitude"] += [dic["longitude"]]
                                    dic_papers[author_id][work_id]["latitude"] += [dic["latitude"]]



                        dic_encoding[author_id][work_id] = {}

                        try:
                            if line[1] != None:
                                dic_encoding[author_id][work_id]["encoded_title"] = clean_encoding(line[1])
                            else:
                                dic_encoding[author_id][work_id]["encoded_title"] = None

                        except:
                            dic_encoding[author_id][work_id]["encoded_title"] = None
                            print(author_id , work_id)
                            pass
                        
                        try:
                            if line[2] != None:
                                dic_encoding[author_id][work_id]["encoded_abstract"] = clean_encoding(line[2])
                            else:
                                dic_encoding[author_id][work_id]["encoded_abstract"] = None

                        except:
                            dic_encoding[author_id][work_id]["encoded_abstract"] = None
                            print(author_id , work_id)
                            pass
                        


            good_similarity = 0        
                     
            for work_id in dic_encoding[author_id]:
                
                
                paper = dic_encoding[author_id][work_id]
                
                for inventor_id in PatentsView_id:
                
                    for patent_id in dic_patents[inventor_id]:
                        
                        patent = dic_patents[inventor_id][patent_id]
                        
                        
                        
                        
                        sim_abstract = similarity_abstract(paper , patent)
                        sim_title = similarity_title(paper , patent)
                        
                        if sim_abstract != None and sim_title != None:
                            dic_comparison[author_id][work_id + " " + "US-" +patent_id] = {}
                            dic_comparison[author_id][work_id + " " + "US-" +patent_id]["similarity_abstract"]= sim_abstract
                            dic_comparison[author_id][work_id + " " + "US-" +patent_id]["similarity_title"]= sim_title
                        
                
                
    conn.close()
                
    
    return  dic_papers , dic_patents , dic_comparison
                    
       
        
        
#get the patents associated with the patent numbers stored in the dictionary dic_ids


def get_papers2( dic_ids , dic_missing_ids , dic_papers):
        
    #establishing the connection
    conn = psycopg2.connect(database="spec1142", user=user , password=password , host="192.168.100.54")

    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    

    for names in dic_ids:
        
        author_name = names.split("%")[0]
        set_author_ids = dic_ids[names]["OpenAlex_id"]
        for author_id in set_author_ids:
                        
            if author_id in dic_papers and "co-authors" not in dic_papers[author_id]:
                
                for work in dic_papers[author_id]:

                    text = """SELECT  w.work_id , 
                                      w.publication_date , 
                                      w.concepts , 
                                      w.referenced_works,
                                      string_agg( a.display_name , ';') 
                                      


                              FROM works_OpenAlex AS w
                              
                              JOIN works_authors_OpenAlex AS wa ON wa.work_id =  w.work_id 
                              JOIN authors_OpenAlex AS a ON wa.author_id = a.author_id

                              WHERE w.work_id = '""" + work + """'
                              GROUP BY w.work_id,
                                       w.publication_date , 
                                       w.concepts , 
                                       w.referenced_works;"""

                    cursor.execute(text)
                    res = cursor.fetchall()
                

                    for line in res:
                        

                        work_id = line[0]
                        dic_papers[author_id][work_id]["co_authors"] = [ normalize(elem) for elem in set(line[4].split(";")) ] 



                        if line[2] != None:
                            dic_papers[author_id][work_id]["concepts"] = ", ".join(line[2].split("; "))                        
                        else:
                            dic_papers[author_id][work_id]["concepts"] = None


                        if line[3] != None:
                            dic_papers[author_id][work_id]["referenced_works"] = set(line[3].split("; "))
                        else:
                            dic_papers[author_id][work_id]["referenced_works"] = None


                        if line[1] != None:
                            dic_papers[author_id][work_id]["publication_date"] = line[1].year
                        else:
                            dic_papers[author_id][work_id]["publication_date"] = None


                        dic_papers[author_id][work_id]["author_name"] = author_name
                        
                    
            
            
            else:
                print(author_id)

                            
    conn.close()
    

    return dic_papers







#get the features that are representing the similarity between a paper and a patent

def get_dic_test(last_name):
    
    
    #get the author ids, inventor ids, relative papers and patents, and similarity scores between the author and inventor names 
    dic_comparison , dic_ids , dic_authors = get_pd_table_comparison(last_name)[:3]
    
    dic_papers , dic_patents , dic_test_full =  save_time(dic_ids)
    
    dic_papers = get_papers2( dic_ids , dic_missing_ids , dic_papers)
    
    dic_test = {}
    
    for elem in dic_ids:
        
        author_name , inventor_name = elem.split("%")

        list_author_ids = dic_ids[elem]["OpenAlex_id"]

        list_inventors_ids = dic_ids[elem]["PatentsView_id"]
        
        for author_id in list_author_ids:
            
            if author_id in dic_papers:
            
                dic_test = { **dic_test, **dic_test_full[author_id]}


                data_author = dic_papers[author_id]
                list_dates_author = [ data_author[paper]["publication_date"] for paper in data_author if "publication_date" in data_author[paper] and data_author[paper]["publication_date"] != None]
                if list_dates_author != []:
                    dic_dates = { "list_dates" : list_dates_author,
                                     "max_dates" : max(list_dates_author),
                                     "min_dates" : min(list_dates_author),
                                     "mean_dates" : np.mean(list_dates_author),
                                     "chi_dist" : chi2.fit(list_dates_author) } 

                else:
                    dic_dates = None

                data_author_ids = dic_authors[author_id]


                for inventor_id in list_inventors_ids:

                    data_inventor = dic_patents[inventor_id]

                    for patent in data_inventor:

                        data_patent = data_inventor[patent]

                        for paper in data_author:

                            data_paper = data_author[paper]

                            if paper + " " + "US-" +patent in dic_test:
                                

                                if dic_test[paper + " " + "US-" +patent]["similarity_title"] == None or dic_test[paper + " " + "US-" +patent]["similarity_abstract"] == None:
                                    dic_test.pop(paper + " " + "US-" +patent)
                                
                                else:
                                    if "co_authors" in data_paper:
                                        dic_test[paper + " " + "US-" +patent] = comparison_pairs2(dic_test[paper + " " + "US-" +patent] , data_paper , data_patent , data_author_ids , dic_dates)
                                        dic_test[paper + " " + "US-" +patent]["inventor_id"] =  inventor_id
                                        dic_test[paper + " " + "US-" +patent]["author_id"] = author_id
                                        dic_test[paper + " " + "US-" +patent]["author_name"] = data_paper["author_name"]
                                        dic_test[paper + " " + "US-" +patent]["inventor_name"] = data_patent["inventor_name"]
                                        dic_test[paper + " " + "US-" +patent]["name_score"] = dic_comparison[data_paper["author_name"]][data_patent["inventor_name"]]

                                    else:
                                        dic_test.pop(paper + " " + "US-" +patent)

                                
                                
                                #except:
                                    #continue 
            
    dic_test = { k : v for k,v in dic_test.items() if "number_in_common_authors" in v } 

    return dic_test
                        
                                            

        
        

        
        
        

import pickle5 as pickle 

#load the model from disk
rf_filename_distance = main_path + 'train_the_model/random_forest_distance.sav'
random_forest_distance = pickle.load(open(rf_filename_distance, 'rb'))

rf_filename_no_distance = main_path + 'train_the_model/random_forest_no_distance.sav'
random_forest_no_distance = pickle.load(open(rf_filename_no_distance, 'rb'))




def prediction(func_input):

    name , filelocation , filewrite = func_input
    
    dic_res = get_dic_test(name)
    
    dic_pred_dist = { ids : { k : dic_res[ids][k] for k in ['number_in_common_authors', 'similarity_title', 'similarity_abstract', 'distance_assignees', 'distance_inventors', 'in_common_citing_papers','similarity_institution', 'date_likelihood', 'date_difference']} for ids in dic_res if pd.isna(dic_res[ids]["distance_assignees"]) == False and  pd.isna(dic_res[ids]["distance_inventors"]) == False }
    dic_pred_no_dist = { ids : { k : dic_res[ids][k] for k in ['number_in_common_authors', 'similarity_title', 'similarity_abstract',  'in_common_citing_papers','similarity_institution', 'date_likelihood', 'date_difference']} for ids in dic_res if pd.isna(dic_res[ids]["distance_assignees"]) == True or  pd.isna(dic_res[ids]["distance_inventors"]) == True }

    res_dist = np.array([ list(item.values()) for item in list(dic_pred_dist.values()) ])
    res_no_dist = np.array([ list(item.values()) for item in list(dic_pred_no_dist.values()) ])
    
    if len(res_no_dist) > 0:
        no_dist_pred = random_forest_no_distance.predict_proba(res_no_dist)[:,1]
    else:
        no_dist_pred = []
    
    if len(res_dist) >0:
        dist_pred = random_forest_distance.predict_proba(res_dist)[:,1]
    else:
        dist_pred = []
        

    keys = list(dic_pred_dist.keys())
    for k in range(len(keys)):
        dic_res[keys[k]]["prediction"] = dist_pred[k]

    keys = list(dic_pred_no_dist.keys())
    for k in range(len(keys)):
        dic_res[keys[k]]["prediction"] = no_dist_pred[k]

    dic_results = { k : v for k,v in dic_res.items() if v["prediction"] + v["name_score"]**2 > 1.25}
    results = np.array([ [ v["author_id"], v["inventor_id"] ] for v in dic_results.values() ])
    

    dic_final = {}
    
    
    for line in dic_results:
        author_id = dic_results[line]["author_id"]
        inventor_id = dic_results[line]["inventor_id"]
        if inventor_id + " " + author_id not in dic_final:
            dic_final[inventor_id + " " + author_id] = {}
            dic_final[inventor_id + " " + author_id]['inventor_id'] = inventor_id
            dic_final[inventor_id + " " + author_id]['author_id'] = author_id
            dic_final[inventor_id + " " + author_id]['inventor_name'] = dic_results[line]["inventor_name"]
            dic_final[inventor_id + " " + author_id]['author_name'] = dic_results[line]["author_name"]
            dic_final[inventor_id + " " + author_id]['number of match'] = 0
            dic_final[inventor_id + " " + author_id]["name score"] = dic_results[line]["name_score"]
        dic_final[inventor_id + " " + author_id]['number of match'] += 1
        
            
            
    for line in dic_final:
        author_id = dic_final[line]["author_id"]
        inventor_id = dic_final[line]["inventor_id"]
        count = len({ k:v for k,v in dic_res.items() if v["author_id"] == author_id and v["inventor_id"] == inventor_id})
        dic_final[line]["number of comparison"] = count


    df_final = pd.DataFrame(dic_final , index = [ 'inventor_id' , "author_id", "number of comparison", "number of match", "author_name" , "inventor_name" , "name score"]).T    

    df_final.to_csv(filelocation , sep='\t' , mode = "a" , index  = False, header = False )

    
    file_object = open(filewrite, 'a')
    file_object.write(name + "\n")
    file_object.close()





    
############################## Function to run to run the entire code #########################################################


## load the names that are already done (stored in the folder "run_SI_dataset/Names"
files_names = glob.glob(main_path + "run_SI_dataset/Names/name_matched_*")

names = set()
for file in files_names:
    file_text = open(file , "r")
    for line in file_text:
        names.add(line.replace("\n" , "").lower())



def multi_prediction(i):
    
    ## write in a file when the thread starts and ends 
    file_monitor = main_path + "run_SI_dataset/Monitor/monitor_" + str(i) + ".txt"
    file_object = open(file_monitor, 'a')
    file_object.write("start" + "\n")
    file_object.close()
    

    ## identify names for which the process wss not applied yet
    errors = {'junior', 'senior', 'sr'}
    list_names = list(set(list(dic_last_names.keys())[8000:]) - names - errors) 

    list_names.sort()

    
    filename = main_path + "run_SI_dataset/test/gatekeepers_" + str(i) +  ".tsv"
    filewrite = main_path + "run_SI_dataset/test/name_matched_" + str(i) +  ".txt"

    
    func_inputs = [ ( list_names[k].title() , filename , filewrite  ) for k in range(i , len(list_names) , workers) ]

    ## write the number of names that are being done in the monitoring file 
    file_object = open(file_monitor, 'a')
    file_object.write(str(len(func_inputs)) + "\n")
    file_object.close()
    

    ## for each name, apply the process. If the process fail, write the name in the error file. 
    for func_input in func_inputs:
        if func_input[0] not in names:
            
            try:
            
                res = prediction( func_input )
            
            except:
                
                file_error = main_path + "run_SI_dataset/Errors/name_matched_errors_" + str(i) + ".txt"
                file_object = open(file_error, 'a')
                file_object.write(func_input[0] + "\n")
                file_object.close()

    file_object = open(file_monitor, 'a')
    file_object.write("done" + "\n")
    file_object.close()
              


############################## Run function with parallelization #########################################################
############################### two ways to parallelize the code: #########################################################


## 1) slurm with MPI 
#multi_prediction(MPI.COMM_WORLD.Get_rank() )



## 2) multiprocessing in python 
import warnings      
from multiprocessing import Process

workers = 12

if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter("ignore",UserWarning)
        
        processes = [Process(target=multi_prediction, args=(k,)) for k in range(workers)]
        
        for process in processes:
            process.start()
            
        for process in processes:
            process.join()

    


