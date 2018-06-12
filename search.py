import csv
import os
import re
import requests
import urllib

################################################################################
#
#  EDIT HERE
#
################################################################################

parameters = {
    'author': 'Sands, Emily Glassberg',
    # 'title': 'global warming',
    'subject': 'economics'
}
outfile = 'results.csv'
fields = ['Advisor', 'Committee member', 'University/institution', 'Department', 'Degree']

################################################################################
#
#  STOP EDITING HERE (PROBABLY)
#
################################################################################

# form and escape query, e.g. 'title="global warming" AND author=Castet'
# which becomes 'title%3d%22global%20warming%22%20AND%20author%3dCastet'
query = ''
for key in parameters:
    query += key + '="' + parameters[key] + '" AND '
query = urllib.quote(query[:-5])
# form entire URL
URL1 = 'http://fedsearch.proquest.com/search/sru/pqdtglobal?operation=searchRetrieve&version=1.2&query=' + query
# this will match to any links to abstract pages (which contain the info we want)
URL2_regex = re.compile('https:\/\/search.proquest.com\/docview\/[0-9]*\/abstract.*fedsrch')
# execute search
response1 = requests.get(URL1)
# get all links that match the abstract pages
abstract_URLs = re.findall(URL2_regex, response1.text)
print "Number of results: " + str(len(abstract_URLs))
# if the file exists, we won't add new headers later
file_exists = os.path.exists(outfile)
with open(outfile, 'a') as out:
    writer = csv.DictWriter(out, fieldnames=fields)
    if not file_exists:
        writer.writeheader()
    line = {}
    # for all the URLs to abstracts we found:
    for URL2 in abstract_URLs:
        # request the abstract
        r2 = requests.get(URL2)
        # try to get the data for each field
        for field in fields:
            try:
                junk = re.search(field + ' (<.*?>)+', r2.text)
                end = re.search('class="display_record_indexing_row"', r2.text[junk.end():])
                line[field] = re.findall('>[a-zA-z,. ();]+<', '>' + r2.text[junk.end() : junk.end() + end.start()])
                line[field] = map(lambda x: x[1:-1].encode('ascii'), line[field])
            except:
                line[field] = ''
        writer.writerow(line)


