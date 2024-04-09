# This folder describes how the process to link scientists (from OpenAlex) to inventors (from PatentsView). 

Here, we provide the code to create the SI dataset.

This section requires the full data (OpenAlex + PatentsView) to be loaded in a Postgres database (username and password are required to run the codes, please see folder download_OpenAlex and download_PatentsView). It also requires the patent and paper titles and abstracted to be encoded with a pre-trained model (please see folder text_encoding), and the section "train_the_model" to be run to save the predictive classification models. 

* The jupyter notebook "SI_dataset.ipynb" provides the code to test the full SI identification process. The first section provides the code to generate the first and last name frequency dictionaries based on name frequency in PatentsView database. The next section provides the code to test the full SI identification process on a given last name. It provides examples of SIs named  "Doudna" or "Scharfmann". The third section describes how to run the full process on the entire databases. Finally, the last section provides the code to clean the SI dataset and to remove the inconsistencies. 


* The two python files "gatekeepers_uncommon_names.py" and "gatekeepers_common_names.py" provide the code to run the SI identification process on all PatentsView last names. Note that, for very common last names, the RAM memory tends to blow up. Therefore, two python files are provided. 
    * Start with "gatekeepers_uncommon_names.py", which runs the process on all last names, except the 8,000 most common last names. The parallelization is coded such that each CPU runs one last name. 
    * Then, use "gatekeepers_common_names.py" to run the remaining last names. "gatekeepers_common_names.py". The parallelization is coded such that the last names go into the process one by one. Then, each CPU runs one first name. It allows the very common last names to be cut into pieces and avoid exceeding the RAM memory.
 
* The results of the identification process will be stored in a folder "Results". The names already processed will be stored in text files in a folder "Names". The names raising errors will be stored in a folder "Errors". Text files indicating the start, the number of names processed by the CPU and the end of the job running on the CPU will be written in a folder "Monitor".
