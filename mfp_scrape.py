# import necessary libraries 
from bs4 import BeautifulSoup 
import requests 
import re
import csv
import sys
from mfp_request import getHTMLdocument
from myfitnesspal.client import Client
from pals import palList
import datetime
  
def scrape_mfp(myDate, myPals):
    myClient = Client()
    print(myClient.user_id)
    print(myClient.effective_username)
    palData = []
    for myPal in palList:
        try:
            palDatum = {}
            palDatum['Name'] = myPal
            palDatum['Goal'] = myClient.get_date(myDate, friend_username=myPal)._goals
            palDatum['Goal'] = myClient.get_date(myDate, friend_username=myPal)._goals['calories']
            palDatum['Calories'] = myClient.get_date(myDate, friend_username=myPal).totals['calories']
            palData.append(palDatum)
        except Exception as e:
            print('Error pulling data for [{0}]'.format(myPal))
            print(e)
    return palData


def write_report(filename, palData):
    myDate = datetime.datetime.today()
    markdownLines = []
    markdownLines.append('# Report {0}\n'.format(myDate.strftime('%m-%d-%Y')))
    return markdownLines

myDate = datetime.date(
            int(2024),
            int(11),
            int(13),
        )
palData = scrape_mfp(myDate, palList)
print(write_report('temp.md', palData))
