# import necessary libraries 
from bs4 import BeautifulSoup 
import requests 
import re
import csv
import sys
from myfitnesspal.client import Client
from pals import palList
import datetime
import traceback
  
def scrape_mfp(myDate, myPals):
    myClient = Client()
    print('Scraping Website for users [{0}] on date [{1}]'.format(myPals, myDate), flush=True)
    palData = []
    for myPal in palList:
        try:
            palDatum = {}
            myDay = None
            if ' :muscle:' in myPal: #Muscle emoji in username triggers protein goal
                palDatum['uname'] = myPal.replace(' :muscle:','')
                myDay = myClient.get_date(myDate, friend_username=palDatum['uname'])
                palDatum['Goal'] = myDay._goals['protein']
                palDatum['GoalType'] = 'protein'
            else: #Default case is calorie goal
                palDatum['uname'] = myPal
                myDay = myClient.get_date(myDate, friend_username=palDatum['uname'])
                palDatum['Goal'] = myDay._goals['calories']
                palDatum['GoalType'] = 'calories'
            palDatum['Name'] = myPal
            #Attempt to pull protein and calorie information for the day
            try:
                palDatum['Calories'] = myDay.totals['calories']
            except:
                palDatum['Calories'] = 0
            try:
                palDatum['Protein'] = myDay.totals['protein']
            except:
                palDatum['Protein'] = 0
            if palDatum['GoalType'] == 'calories':
                #Calorie goals need to be compared against there goal WITHOUT including excersise offset.
                #So we need to remove the excersise offset from the goal
                try:
                    palDatum['Excercises'] = myDay.exercises
                    for excercise in palDatum['Excercises']:
                        for myexcercise in excercise.get_as_list():
                            try:
                                palDatum['Goal'] -= myexcercise['nutrition_information']['calories burned']
                            except:
                                pass
                except:
                    pass
            try:
                #Track dinner specifically for 'warning' purposes
                for meal in myDay.meals:
                    if meal.name.lower() == 'dinner':
                        palDatum['Dinner'] = meal.totals['calories']
            except:
                palDatum['Dinner'] = 0
            palDatum['Weblink'] = 'https://www.myfitnesspal.com/food/diary/'+palDatum['uname']+'?date='+myDate.strftime('%Y-%m-%d')
            #If calorie/protein goal fails, or no calories tracked, marked FAIL
            #If dinner is missed, or we are suspiciously low on logged calories, mark WARN
            palDatum['Status'] = 'OK'
            if palDatum['Calories'] < (palDatum['Goal'] * .8) or palDatum['Dinner'] < 1:
                palDatum['Status'] = 'WARN'
            if palDatum['GoalType'] == 'calories' and palDatum['Calories'] > palDatum['Goal']:
                palDatum['Status'] = 'FAIL'
            elif palDatum['GoalType'] == 'protein' and palDatum['Protein'] < palDatum['Goal']:
                palDatum['Status'] = 'FAIL'
            elif palDatum['Calories'] < 1:
                palDatum['Status'] = 'FAIL'
            palData.append(palDatum)
        except Exception as e:
            print('Error pulling data for [{0}]'.format(palDatum['uname']))
            print(traceback.format_exc())
            print(e)
    return palData

def write_emoji(status):
    if status == 'OK':
        return ':heavy_check_mark:'
    if status == 'WARN':
        return ':warning:'
    if status == 'FAIL':
        return ':no_entry_sign:'

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
        #First cell of table is the user's name
        markdownLines.append(' '+pal+' |')
        myCount = 0
        for myDate in palData:
            if myDate == dates[myCount]:
                for myEntry in palData[myDate]:
                    #Find the relevant entry for this table row (based on user name)
                    if myEntry['Name'] == pal:
                        #Cell includes data for goal for this day (either calorie or protein goal)
                        if myEntry['GoalType'] == 'protein':
                            markdownLines.append(' ['+str(int(myEntry['Protein']))+' / '+str(int(myEntry['Goal']))+']('+myEntry['Weblink']+') '+write_emoji(myEntry['Status'])+' |')
                        else:
                            markdownLines.append(' ['+str(int(myEntry['Calories']))+' / '+str(int(myEntry['Goal']))+']('+myEntry['Weblink']+') '+write_emoji(myEntry['Status'])+' |')
                        myCount += 1
        markdownLines.append('\n|')
        
    with open(filename, "w") as txt_file:
        for line in markdownLines:
            txt_file.write(line)
    return markdownLines

myDate = datetime.datetime.today()
number_of_days = 7
palData = {}
for i in range(number_of_days):
    myDate = myDate - datetime.timedelta(days=1)
    palDatum = scrape_mfp(myDate, palList)
    palData[myDate.strftime('%m-%d-%Y')] = (palDatum)

print(palData)
print(write_report('temp.md', palData, palList))
