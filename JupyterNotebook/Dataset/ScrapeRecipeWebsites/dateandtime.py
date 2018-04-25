'''
Created on 22 Jan 2015

@author: David
'''
from collections import Set
from datetime import date, datetime, timedelta
import calendar
import logging
import re

from dateutil.parser import parse as dateparse

STRIPTODIGITS = re.compile("[^0-9 ]")
REPLACECHARDATECHARS = re.compile("[^a-zA-Z0-9 "+re.escape(":")+"]")
STRIPTOCHARDATEDIGITS = re.compile("[^a-zA-Z0-9 "+re.escape("\\/:-,.")+"]")

FIRSTVALIDDATE = datetime(2000, 1, 1)
LASTVALIDDATE = datetime(2050, 1, 1)
MONTHS = set([m[:3] for m in calendar.month_name[1:]])
YEARS = set([str(2000+y) for y in range(0,20)])
SHORTYEARS = set([str(y) for y in range(0,20)])
def parseddate(node, defaulttime = None):
    try:
        txt = re.sub(STRIPTODIGITS, ' ', node)
        if len(txt.strip()) < 3:
            return None
        for month in MONTHS:
            if month in node or month.upper() in node:
                try:
                    txt = re.sub(REPLACECHARDATECHARS," ",re.sub(STRIPTOCHARDATEDIGITS, '', node))
                    monthpos = txt.find(month)
                    if monthpos > 0:
                        txt = re.sub(STRIPTODIGITS," ",re.sub(STRIPTODIGITS, ' ', txt[:monthpos])) + txt[monthpos:]
                    asplit=txt[monthpos-5 if monthpos-5 > -1 else 0:].split()
                    if len(asplit) > 2:
                        try:
                            adate=dateparse(" ".join(asplit[:3]))
                            if adate is not None and FIRSTVALIDDATE < adate and adate < datetime.now():
                                return adate
                        except:
                            pass
                    asplit=txt[monthpos-3 if monthpos-3 > -1 else 0:].split()
                    if len(asplit) > 2:
                        try:
                            adate=dateparse(" ".join(asplit[:3]))
                            if adate is not None and FIRSTVALIDDATE < adate and adate < datetime.now():
                                return adate
                        except:
                            pass
                    asplit=txt[monthpos:].split()
                    if len(asplit) > 2:
                        adate=dateparse(" ".join(asplit[:3]))
                        if adate is not None and FIRSTVALIDDATE < adate and adate < datetime.now():
                            return adate
                except:
                    pass
        if "20" in node:
            try:
                yearpos = txt.find("20")
                year = txt[yearpos:yearpos+4]
                if year in YEARS:
                    splittxt = txt.strip().split()
                    if len(splittxt) > 2:
                        sdate = " ".join(splittxt[:3])
                        if len(sdate) > 4:
                            adate = dateparse(sdate)
                            if adate is not None and FIRSTVALIDDATE < adate and adate < datetime.now():
                                return adate
                    dateserial = txt[yearpos:yearpos+8]
                    if len(dateserial) == 8 and dateserial.isdigit():
                        adate = dateparse(dateserial)
                        if adate is not None and FIRSTVALIDDATE < adate and adate < datetime.now():
                            return adate
            except:
                pass
        tdate = node.split("T")[0].split()[0]
        if len(tdate) > 10:
            return
        digittxt = re.sub(STRIPTODIGITS, '', tdate)
        if len(digittxt) > 2:       
            txt = re.sub(STRIPTOCHARDATEDIGITS, '', tdate)
            if len(txt)> 7:
                stxt = txt[txt.find(digittxt[0]):]
                if len(stxt) > 7:
                    adate = dateparse(stxt)
                    if adate is not None and FIRSTVALIDDATE < adate and adate < datetime.now():
                        return adate        

        return defaulttime
    except:
        return defaulttime
    
def invalidperiod(adate):    
    if adate is not None and FIRSTVALIDDATE < adate and adate < datetime.now():
        return adate        

def parsedtime(node):
    pass

def formatRfc3339(t):
    return t.strftime('%Y-%m-%dT%H:%M:%S.%fZ')


