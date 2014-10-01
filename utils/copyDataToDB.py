# -*- coding: utf-8 -*-
#Download the index file and all cities
import urllib
import unicodecsv as csv
import os
import psycopg2

import metautils

validsources = ('m', 'd', 'c', 'g', 'b')

def reformatdata(cityname):
    mapping = dict()
    mapping['city'] = u'Stadt'
    mapping['source'] = u'Quelle'
    mapping['title'] = u'Dateibezeichnung'
    mapping['description'] = u'Beschreibung'
    mapping['temporalextent'] = u'Zeitlicher Bezug'
    mapping['licenseshort'] = u'Lizenz'
    mapping['costs'] = u'Kosten'
    mapping['publisher'] = u'Veröffentlichende Stelle'

    dictsdata = dict()

    with open(cityname + '.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            source = row['Quelle'].strip()
            if source not in validsources:
                print 'Error: ' + file + ' has missing or unrecognised source(s)'
                exit()
            else:
                if source not in dictsdata:
                    dictsdata[source] = []
                dictsdata[source].append(row)
            
    takenrows = dict()

    for source in validsources:
        if source in dictsdata:
            print 'Processing source: ' + source
            for row in dictsdata[source]:
                theurl = ''
                
                url = row['URL Datei'].strip()
                parent = row['URL PARENT'].strip()           
                print 'Processing entry with parent [' + parent +'] and url [' + url + ']'

                if url != '' and parent == '':
                    theurl = url
                else:
                    theurl = parent

                #Parents are always favoured and should be unique
                #We assume that all catalog and manual entries are unique
                #Otherwise we rather aggressively expect the filenames to be unique;
                #often there is more than one way to the same file
                if (theurl not in takenrows) or source == 'd' or source == 'm':
                    print 'Adding ' + theurl 
                    row['URL'] = theurl
                    if theurl == parent and url != '':
                        row['filenames'] = [url]
                    else:
                        row['filenames'] = []
                    takenrows[theurl] = row
                else:
                    print 'Not adding: url already there, transferring filename, categories and geo'
                    if url != '':
                        takenrows[theurl]['filenames'].append(url)
                    for key in row:
                        if row[key].strip().lower() == 'x':
                             takenrows[theurl][key] = 'x'

    con = None
    
    try:
        con = psycopg2.connect(database='odm', user='postgres', password='p0stgre5', host='127.0.0.1')
        cur = con.cursor()
        for row in takenrows.values():
            formats = metautils.csvtoarray(row['Format'].upper())
            
            categories = []
            geo = False
            
            for key in row:
                if not(type(row[key]) == list):
                    if row[key].strip().lower() == 'x':
                        if key.strip().lower() == 'geo':
                            geo = True
                        else:
                            categories.append(key)
            checked = True #All of this data is 'open data'
            accepted = False #Validation - inter source deduplification has NOT been performed
            cur.execute("INSERT INTO data \
                (city, source, url, title, formats, description, temporalextent, licenseshort, costs, publisher, spatial, categories, checked, accepted, filelist) \
                SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s \
                WHERE NOT EXISTS ( \
                    SELECT url FROM data WHERE url = %s \
                )",
                (cityname, row[mapping['source']].strip(), row['URL'], row[mapping['title']].strip(),
                formats, row[mapping['description']].strip(), row[mapping['temporalextent']].strip(),
                row[mapping['licenseshort']].strip(), row[mapping['costs']].strip(),
                row[mapping['publisher']].strip(), geo, categories, checked, accepted, row['filenames'], row['URL'])
                )
    except psycopg2.DatabaseError, e:
        print 'Database error: %s' % e
        exit()
    finally:
        if con:
            con.commit()
            con.close()
           
kurznamecolumn = 'kurzname'
gidcolumn = 'GID in Datenerfassung'

indexkey = os.environ['INDEXKEY']
erfassungkey = os.environ['ERFASSUNGKEY']

iurl = "https://docs.google.com/spreadsheets/d/" + indexkey + "/export?gid=0&format=csv"
print "Downloading index of cities to index.csv using url " + iurl + "..."
urllib.urlretrieve (iurl, "index.csv");

print "Parsing list of cities to download each file..."

with open('index.csv', 'rb') as csvfile:
    cityreader = csv.DictReader(csvfile, delimiter=',')
    indexfields = cityreader.fieldnames
    
    #For each city that has a short name, download its data from the other sheet, if we have the gid
    for row in cityreader:
        if row[kurznamecolumn] != "":
          if row[gidcolumn] != "":
              durl = "https://docs.google.com/spreadsheets/d/" + erfassungkey + "/export?gid=" + row[gidcolumn] + "&format=csv"
              print "Downloading data for " + row[kurznamecolumn] + " using url " + durl + "..."
              urllib.urlretrieve (durl, row[kurznamecolumn] + ".csv");
              reformatdata(row[kurznamecolumn])
          else:
              print "No gid for this city, please check spreadsheet"

