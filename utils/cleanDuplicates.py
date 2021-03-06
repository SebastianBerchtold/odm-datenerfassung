import unicodecsv as csv
import sys

if (len(sys.argv)<3):
    print 'Usage: cleanDuplicates filetoclean.csv outputfile.csv [supportingitemsfulllist.csv]'
    exit()

lowestulmparents = ('/metadaten/', '/single/')

csvoutfile = open(sys.argv[2], 'wb')
citywriter = csv.writer(csvoutfile, delimiter=',')
cities = dict()

with open(sys.argv[1], 'rb') as csvfile:
    cityreader = csv.reader(csvfile, delimiter=',')
    #Skip headings
    headings = next(cityreader, None)
    #Write headings
    citywriter.writerow(headings)

    #Divide up data into cities to reduce searching
    for row in cityreader:
        cityurl = row[0]
        if cityurl not in cities:
            cities[cityurl] = dict()
            
csvfile.close()
    
with open(sys.argv[1], 'rb') as csvfile:
    cityreader = csv.reader(csvfile, delimiter=',')
    #Skip headings
    headings = next(cityreader, None)
    
    for inrow in cityreader:
        try:
            cityurl = inrow[0]
            searchurl = inrow[1]
            parenturl = inrow[6]
        except:
            print u'Data format error: ' + u', '.join(inrow) + u'\nStopping.'
        found = False

        print "Searching for " + searchurl

        if searchurl in cities[cityurl]:
            #Prioritize records with all data
            #In general this shouldn't happen, as the file is downloaded
            #after the link is found
            if ((('ermittelt' in cities[cityurl][searchurl][6]) and ('ermittelt' not in parenturl)) or 
            #Ulm special handling to prevent using links from summary pages
            ((cityurl == 'ulm.de') and any(x in parenturl for x in lowestulmparents))):
                cities[cityurl][searchurl] = inrow
                print "Replacing row"
            else:
                print "Row is already there: duplicate"
        else:
            print "Appending as unique entry"
            cities[cityurl][searchurl] = inrow

findparentsource = False

if (len(sys.argv)>3):
    findparentsource = True
    parentsfile = sys.argv[3]

for city in cities.values():
    for outputrow in city.values():
        if 'ermittelt' in outputrow[6] and findparentsource:
            #These links always have http etc. in them, the stored links from the A elements may not
            missinglink = u'/'.join(outputrow[1].split('/')[3:])
            print 'Searching for link component: ' + missinglink + ' in entire items file'
            #Unfortunately it won't work if the URL arguments get rearranged :(
            #If it becomes a problem we should parse the URLs
            with open(sys.argv[3], 'rb') as csvfile:
                parentreader = csv.reader(csvfile, delimiter=',')
                #Skip headings
                headings = next(parentreader, None)

                for inrow in parentreader:
                    try:
                        fileurl = inrow[1]
                    except:
                        print inrow
                        fileurl = ''
                    if missinglink in fileurl and 'ermittelt' not in inrow[6]:
                        print 'FOUND'
                        outputrow[2] = inrow[2]
                        outputrow[6] = inrow[6]
                        outputrow[7] = inrow[7]      
                        break
        citywriter.writerow(outputrow)

csvfile.close();
csvoutfile.close();
