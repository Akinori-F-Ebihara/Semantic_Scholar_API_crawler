# SS_crawler

## 0. Summary
Using the Semantic Scholar API, this script searches scientific papers with customized queries.
### Tested environments
- Mac OSX / RaspberryPi
- python 3.5

## 1. Quickstart
### (i)  One-shot execution  
Run once by providing arguments. The usage is:  

 `python SS_crawler.py -o -k your+keywords -N 3 `

options:
-o: one-shot option  
-k: Search keywords concatenated with + sign  
-N: Number of posted papers per search  

### (ii) Periodic execution  
Simply omit the `-o` option to run periedically at the specified date and time.  
The best practice is to run the script on a network-connected server such as RaspberryPi.

 `python SS_crawler.py -k your+keywords -N 3 `

To modify the date and time, change the variable `day_off` and `posting_hour` at the header of the `SS_crawler.py`.  
See 3. Details for more advanced options.

## 2. Background and Motivation
Semantic Scholar [1] is a machine-learning assisted publication search engine. The advantages of using the Semantic Scholar include but not limited to:  
- Search across journal/conference papers in addition to preprint servers (e.g., arXiv, bioRxiv, and PsyArXiv).
- Each paper comes with a list of articles that are highly influenced (thus, highly related) by the paper.
- Recent-updated Semantic Scholar API [2] provides an easy access to the search engine with a customized code.


## 3. Details   
### 3-1. Modifying the default query list  
### 3-2. Slack posting option  
### 3-3. Classic paper searching option  
### 3-4. Default number of papers to be displayed  
### 3-5. Clear the search log  
SS_crawler saves the IDs of the papers that are already posted as `.pkl` files.  
The IDs of the papers and classic papers are saved as `published_ss.pkl` and `published_ss_old.pkl`, respectively.  
To clear the history, simply delete these files. If a specific paper ID must be deleted, the ID needs to be deleted from the `.pkl` file.
Note that this function is adapted from the arXiv API crawler found at [3].  

## References
[1] https://www.semanticscholar.org   
[2] https://www.semanticscholar.org/product/api  
[3] https://github.com/kushanon/oreno-curator/   
