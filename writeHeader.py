# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 13:27:18 2020

@author: mns72
"""

def main(outString, width=60):
    if width < len(outString):
        padding = 20;
    else:
        padding = round((width - len(outString))/2)
        outString = padding*"*" + " " + outString.upper() + " " + padding*"*"
        print("\n" + len(outString)*"*")
        print(outString)
        print(len(outString)*"*")