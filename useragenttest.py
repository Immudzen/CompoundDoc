#!/usr/bin/env python2.1

from useragent import UserAgent
import time

list = open('browsers', 'r').readlines()
start = time.time()
list = [(UserAgent(agentString=i).agent, i) for i in list]
stop = time.time()
print stop-start, len(list)
