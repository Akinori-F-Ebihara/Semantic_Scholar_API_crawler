#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov. 21st, 2021

@author: Akinori F. Ebihara

"""

import numpy as np
import requests
import re
import pickle
import os
from datetime import datetime 
import time
import calendar
import argparse
# import pdb # for debug

#------------------------USER DEFINED PARAMETERS START-----------------------------------
# Slack API url to your channel. Modify here!
slack_url = ''

# SemanticScholar API url for searching
ss_url = 'http://api.semanticscholar.org/graph/v1/paper/search?'
API_key = 'sjTQHQoGMQ1XLIWZKctN65uxxXakd78w1h0elXon'

# Number of papers to be displayed per search
Npapers_to_display = 1
Nclassic_to_display = 1

# Nuber of papers that are analyzed per a loop
Npapers_batch_size = 100 # max 100

# information to be acquired
fields = ('authors', 'paperId', 'externalIds', 'url', 'title', 'abstract', 'venue', 'year', \
          'referenceCount', 'citationCount', 'influentialCitationCount', \
          'isOpenAccess', 'fieldsOfStudy', )

# query for latest papers on daily basis
query_list = ('sequential+density+ratio+estimation', 
              'flash+face+spoofing+detection'
             )

# query for classic papers, one will be randomly chosen
classic_query_list = ('neuroscience',
                      'machine+learning')
ifClassic = True

# year range will be randomly chosen from here
range_classic = np.arange(1935, 2025, 10)

# The time when you want the result (under the periodic execution mode)
posting_hour = 7

# If you have kid(s), shouldn't work on weekends perhaps
day_off = ('Tuesday', 'Thursday', 'Saturday', 'Sunday')

#------------------------USER DEFINED PARAMETERS START------------------------------------


def generate_ss_url(ss_url_, query_, fields_, batch_size_, start_):

    # Compile Semantic Scholar API url
    fullfields = ''
    for targfield in fields_:
        fullfields += targfield + ','
        
    return ss_url_ + 'query={}&fields={}&limit={}&offset={}'.format(
                query_, fullfields[:-1], batch_size_, start_)
        

def entry_splitter(data_):
    
    # Split the returned entry into papers
    pattern = '(\"paperId[\s\S]*?}]})'
    return re.findall(pattern, data_)

        
def entry_parser(data_, fields_):

    # Parse the paper text data into subfields
    datapool = []
    for targentry in data_:
        strpool = []

        for targfield in fields_:
            if 'externalids' in targfield.lower():
                pattern = '\"' + targfield + '\": ({[\s\S]*?})'
            elif 'authors' in targfield.lower() or 'fieldsofstudy' in targfield.lower():
                pattern = '\"' + targfield + '\": \[([\s\S]*?)\]'
            elif 'title' in targfield.lower() or 'abstract' in targfield.lower():
                pattern = '\"' + targfield + '\": \"([\s\S]*?)\"'
            else:
                pattern = '\"' + targfield + '\": ([\s\S]*?),'
                
            tmpstr = re.findall(pattern, targentry)
        
            if 'count' in targfield.lower() or 'year' in targfield.lower():
                if 'null' not in tmpstr[0]:
                    tmpstr = int(tmpstr[0])
            elif 'authors' in targfield.lower():
                pattern = '\"name\": \"([\s\S]*?)\"'
                tmpstr = re.findall(pattern, targentry)
                tmpstr2 = ''
                for targ in tmpstr:
                    tmpstr2 += targ + ', '
                tmpstr = tmpstr2[:-2]
            else:
                if not tmpstr:
                    tmpstr = 'none'
                else:
                    tmpstr = tmpstr[0].replace('"', '').strip('[').strip(']')

            strpool.append(tmpstr)
        datapool.append(strpool)
    return np.array(datapool)


def slack_poster(slack_url_, message_):
    # Post the results to your Slack channel
    print(message_)
    if slack_url_ == '':
        return    
    requests.post(slack_url_, json={"text": message_})

    
def ss_crawler(session_, slack_url_, ss_url_, published_ids_, query_list_, fields_,
            Npapers_to_display_, Npapers_batch_size_, 
            range_classic_=[]):

    # Randomly select one query and year range for classic papers
    if not len(range_classic_) == 0:
        query_list_ = (query_list_[np.random.permutation(len(query_list_))[0]],)
        year_dice = np.random.permutation(len(range_classic_) - 1)[0]
    
    for query_ in query_list_:
        
        name = query_.replace('+', ' ')
        
        if not len(range_classic_) == 0:
            classicinfo = '\n'.join(['--------------------',
                                    'Today\'s Classic paper!',
                                     'Year range: {} to {}'.format(
                                         range_classic_[year_dice], range_classic_[year_dice+1] - 1),
                                     'Query: {}'.format(name)
                                    ])
            slack_poster(slack_url, classicinfo)
        else:
            slack_poster(slack_url, "--------------------\nPosting papers of \"{}\"...".format(name))
            
        start = 0
        counter = 0
        continueflag = True
        
        while continueflag:

            ss_url_cooked = generate_ss_url(ss_url_, query_, fields_, Npapers_batch_size_, start)

            textdata = session_.get(ss_url_cooked).text
            parsed_text = entry_splitter(textdata)
            summary = entry_parser(parsed_text, fields_)

            for targpaper in summary:

                # Get the paper identifier
                paperID = targpaper[fields_.index('paperId')]

                if paperID not in published_ids_:
                    
                    if not len(range_classic_) == 0:
                        if 'null' in str(targpaper[fields_.index('year')]):
                            continue
                        paperyear = int(targpaper[fields_.index('year')])
                        if paperyear < range_classic_[year_dice] or \
                            range_classic_[year_dice + 1] <= paperyear:
                            continue

                    # Compile the string to be posted on Slack.
                    # Modify here if you need other information
                    paperinfo = "\n".join(["=" * 10, 
                                           "No." + str(counter + 1), 
                                           '*' + targpaper[fields_.index('title')] + '*', 
                                           targpaper[fields_.index('authors')],
                                           targpaper[fields_.index('url')], 
                                           targpaper[fields_.index('venue')] + ' ' +\
                                           str(targpaper[fields_.index('year')]) + ' / ' + \
                                           targpaper[fields_.index('fieldsOfStudy')] + '\n',
                                           targpaper[fields_.index('abstract')] + '\n',
                                           '#citation: ' + str(targpaper[fields_.index('citationCount')]) + \
                                           ', #influence: ' + str(targpaper[fields_.index('influentialCitationCount')]),
                                          ])

                    slack_poster(slack_url_, paperinfo)

                    # remember the posted paper IDs
                    published_ids_.append(paperID)

                    # limit posts per topic per day
                    counter += 1
                    if counter == Npapers_to_display_:
                        continueflag = False
                        break

            if counter == 0 and len(summary) < Npapers_batch_size_:
                # Reached the end of batch and there aren't any other papers available
                slack_poster(slack_url_, 'No matched unposted papers...')
                continueflag = False
                break
            elif counter == 0 and len(summary) == Npapers_batch_size_:
                # If the end of batch is reached but still other papers are remaining
                start = start + 100    
    
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='This is a Semantic Scholar crawler that search papers with custom keywords.')
    parser.add_argument('-q', '--query', nargs='*')
    parser.add_argument('-N', '--Npapers', type=int, default=1)
    parser.add_argument('-o', '--once', action='store_true')
    parser.add_argument('-c', '--classic', action='store_true')
    args = parser.parse_args()

    # overwrite parameters if provided
    if args.query:
        query_list = args.query
    if args.Npapers:
        Npapers_to_display = args.Npapers
    if args.once:
        ifClassic = False
    if args.classic:
        ifClassic = True
        
    # load the list of published papers to avoid duplication
    if os.path.exists("published_ss.pkl"):
        published_ids = pickle.load(open("published_ss.pkl", 'rb'))
    else:
        published_ids = []
    if os.path.exists("published_ss_old.pkl"):
        published_ids_old = pickle.load(open("published_ss_old.pkl", 'rb'))
    else:
        published_ids_old = []
        
    # initialize a session, set the API_key as an x-api-key header
    session = requests.Session()
    session.headers['x-api-key'] = API_key

    while True:
        
        # acquire current day and time
        day = calendar.day_name[datetime.today().weekday()]
        currenthour = datetime.now().hour
        print('current hour: ', currenthour)
        
        if currenthour == posting_hour and day not in day_off or args.once:
            
            start = 0
            
            # Post a greeting to your Slack
            slack_poster(slack_url, 'Hello!!')

            # main crawler function
            ss_crawler(session, slack_url, ss_url, published_ids, query_list, fields,
                       Npapers_to_display, Npapers_batch_size)

            if ifClassic:
                # for classic papers
                ss_crawler(session, slack_url, ss_url, published_ids_old, classic_query_list, fields,
                        Nclassic_to_display, Npapers_batch_size,
                        range_classic_=range_classic)
            
            slack_poster(slack_url, 'Done. Enjoy!')
            
            # Update log of published data
            pickle.dump(published_ids, open("published_ss.pkl", "wb"))
            pickle.dump(published_ids_old, open("published_ss_old.pkl", "wb"))
            
            # break and finish the srcipt if --once flag is on
            if args.once:
                break
            
            time.sleep(3600)
            
        else:
            
            # wait for an hour
            print('waiting for the next posting time...')
            time.sleep(3600)
