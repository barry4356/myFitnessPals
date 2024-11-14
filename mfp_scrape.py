# import necessary libraries 
from bs4 import BeautifulSoup 
import requests 
import re
import csv
import sys
from mfp_request import getHTMLdocument
from myfitnesspal.client import Client
  
  
myClient = Client()
print(myClient.user_id)
print(myClient.effective_username)
sys.exit()

url_to_scrape = "https://www.myfitnesspal.com"
  
# create document 
html_document = getHTMLdocument(url_to_scrape)

print(html_document)
  
# create soap object 
soup = BeautifulSoup(html_document, 'html.parser') 
  
outlinks = []  
# find all the anchor tags with "href"  
# attribute starting with "https://" 
for link in soup.find_all('a',  
                          attrs={'href': re.compile("^https://")}): 
    # display the actual urls 
    #print(link.get('href'))
    outlinks.append(link.get('href'))

all_results = []
#url_to_scrape = "https://www.naplesgolfguy.com/arrowhead-golf/"    
for outlink in outlinks:
    try:
        url_to_scrape = outlink
        #url_to_scrape = "https://www.naplesgolfguy.com/arrowhead-golf/"
        html_document = getHTMLdocument(url_to_scrape) 
        soup = BeautifulSoup(html_document, 'html.parser') 

        data = []
        #table = soup.find('table', attrs={'class':'lineItemsTable'})
        tables = soup.findAll('table')
        for table in tables:
            table_body = table.find('tbody')

            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                data.append([ele for ele in cols if ele]) # Get rid of empty values

        results = {}
        results['clubName']=url_to_scrape.split('/')[-2]
        results['Golf Initiation Fee'] = 0
        results['Annual Golf Dues'] = 0
        results['Other Fee'] = 0
        results['Other Dues'] = 0
        results['SFH Minimum'] = 0
        results['SFH Maximum'] = 0
        results['Condos Minimum'] = 0
        results['Condos Maximum'] = 0
        #print(data)
        found = False
        for element in data:
            #print(element)
            if 'golf' in element[0].lower() and 'initiation' in element[0].lower():
                results['Golf Initiation Fee'] = element[1]
                found = True
            elif 'annual' in element[0].lower() and 'golf' in element[0].lower() and 'dues' in element[0].lower():
                results['Annual Golf Dues'] = element[1]
                found = True
            elif 'single' in element[0].lower() and 'family' in element[0].lower():
                if 'no' not in element[1].lower():
                    results['SFH Minimum'] = element[1].split(' ')[0]
                    results['SFH Maximum'] = element[1].split(' ')[-1]
                found = True
            elif 'condos' in element[0].lower():
                if 'no' not in element[1].lower():
                    results['Condos Minimum'] = element[1].split(' ')[0]
                    results['Condos Maximum'] = element[1].split(' ')[-1]
                found = True
            elif 'fee' in element[0].lower():
                results['Other Fee'] = element[1]
                found = True
            elif 'dues' in element[0].lower():
                results['Other Dues'] = element[1]
                found = True
        #print(results)
        if not found:
            print ('Skipping URL: '+url_to_scrape)
            continue
        all_results.append(results)
        with open('golf_scrape.csv', 'w+', newline='') as csvoutfile:
            fieldnames = results.keys()
            csvwriter = csv.DictWriter(csvoutfile, fieldnames=fieldnames)
            csvwriter.writeheader()
            csvwriter.writerows(all_results)
        print("Processed: "+url_to_scrape)
            
            
    except Exception as e:
        print ('Skipping URL: '+url_to_scrape)
        print (e)
        #sys.exit()