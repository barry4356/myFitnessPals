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
            #palDatum['Goal'] = myClient.get_date(myDate, friend_username=myPal)._goals
            palDatum['Goal'] = myClient.get_date(myDate, friend_username=myPal)._goals['calories']
            palDatum['Calories'] = myClient.get_date(myDate, friend_username=myPal).totals['calories']
            palData.append(palDatum)
        except Exception as e:
            print('Error pulling data for [{0}]'.format(myPal))
            print(e)
    return palData


def write_report(filename, palData, myPals):
    myDate = datetime.datetime.today()
    markdownLines = []
    # Write Report Header
    markdownLines.append('# Report {0}\n'.format(myDate.strftime('%m-%d-%Y')))
    # Start Data Table
    markdownLines.append('| |')
    dates = []
    for day in palData:
        # Write dates as header of table
        markdownLines.append(' '+day+' |')
        dates.append(day)
    markdownLines.append('\n| --- |')
    for day in dates:
        markdownLines.append(' --- |')
    markdownLines.append('\n|')
    for pal in myPals:
        markdownLines.append(' '+pal+' |')
        myCount = 0
        for myDate in palData:
            if myDate == dates[myCount]:
                for myEntry in palData[myDate]:
                    if myEntry['Name'] == pal:
                        markdownLines.append(' '+str(myEntry['Calories'])+'/'+str(myEntry['Goal'])+' |')
                        myCount += 1
        markdownLines.append('\n|')
        
    with open(filename, "w") as txt_file:
        for line in markdownLines:
            txt_file.write(line)
    return markdownLines

myDate = datetime.datetime.today()
number_of_days = 2
palData = {}
for i in range(number_of_days):
    myDate = myDate - datetime.timedelta(days=1)
    palDatum = scrape_mfp(myDate, palList)
    palData[myDate.strftime('%m-%d-%Y')] = (palDatum)

print(palData)
print(write_report('temp.md', palData, palList))
