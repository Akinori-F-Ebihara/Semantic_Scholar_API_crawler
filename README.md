# SS_crawler

## 0. Summary
Using the Semantic Scholar API, this script searches scientific papers with customized queries and post the results to your Slack channel.
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
Best practice is to run the script on a network-connected server such as RaspberryPi.

 `python SS_crawler.py -k your+keywords -N 3 `

To modify the date, change the variable at the header of the `SS_crawler.py`.
See 3. Details for more advanced options.

## 2. Background and Motivation
Semantic Scholar [1] is a publication search engine. It's features including one-sentence summary of a paper, calculation of influential citations, and more. Semantic Scholar covers multiple fields of research and   

Semantic Scholar provides API [3]

## References
[1] https://www.semanticscholar.org  
[2]  
[3] https://www.semanticscholar.org/product/api  
[4] https://github.com/kushanon/oreno-curator/  
