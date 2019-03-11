#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 10:24:35 2018

@author: msobral
"""

import poller
import sys,time

class CallbackStdin(poller.Callback):
    
    def handle(self):
        l = sys.stdin.readline()
        print('Lido:', l)
        
    def handle_timeout(self):
        print('Timeout !')
   
        
cb = CallbackStdin(sys.stdin, 3)

sched = poller.Poller()

sched.adiciona(cb)


sched.despache()