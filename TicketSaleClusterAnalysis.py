#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 13:38:40 2019

@author: DannySwift
"""
#%%
import json
import pandas as pd
from simple_salesforce import Salesforce
import scipy.cluster.hierarchy as sch
from sklearn.cluster import KMeans, AgglomerativeClustering
import yaml

#%%
class Analyzer:
    
    def __init__(self):
        self.config = yaml.safe_load(open('config.yml'))
        self.sf = Salesforce(username=config['username'], 
                        password=config['password'], 
                        security_token=config['security_token'])
        q = self.sf.query("SELECT Name FROM PatronTicket__TicketableEvent__c")
        self.events = [x['Name'].split(' -')[0] for x in q['records']]
        self.nevents = len(self.events)
        self.event_dict = dict((self.events[i], i) for i in range(self.nevents))
        self.bin_dict = dict((i, self.events[i]) for i in range(self.nevents))
    
    
    def get_data(self):
        accountids = [d['Id'] for 
                      d in self.sf.bulk.Account.query("SELECT Id FROM Account")]
        
        def get_tix(acc_id):
            q = self.sf.query("SELECT PatronTicket__ItemDetail__c \
                              FROM PatronTicket__TicketOrderItem__c \
                              WHERE PatronTicket__Account__c = '{}'"
                              .format(acc_id))
            shows = [s['PatronTicket__ItemDetail__c'].split(' -')[0] for 
                     s in q['records']]
            
            return(shows)
        
        
        ticket_hist = dict((acc_id, get_tix(acc_id)) for acc_id in accountids)
        self.ticket_hist = ticket_hist
        
    
    def binarize(self):
        if not self.ticket_hist:
            print("Error: Ticket history not retrieved")
            return
        
        def binarize_point(dp):
            val = [0 for i in range(self.nevents)]
            indices = [self.event_dict[e] for e in dp]
            for i in indices:
                val[i] = 1
            
            return(val)
        
        self.data_points = [binarize_point(dp) for dp in self.ticket_hist.values()]
    
    def check_unused_events(self):
        df = pd.DataFrame(self.bin_dict, columns=self.events)
        print(df.loc[(df == 0).all(axis=0)].columns)
        
    def print_clusters(self, df=self.df, labels):
        for i in range(len(np.unique(labels))):
            print("Cluster {}\n".format(i))
            print("People: " + str(len(df.loc[labels == i])))
            print("Total tix: " + str(df.loc[labels == i].sum().values.sum()))
            print(df.loc[labels == i].sum().sort_values()[-10:])
        
#%% showing unused event objects
