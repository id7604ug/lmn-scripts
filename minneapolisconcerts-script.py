import urllib.request
from bs4 import BeautifulSoup
# This script gets concert information from minneappolisconcerts.net

def main():
    link = "http://www.minneapolisconcerts.net/"
    resp = urllib.request.urlopen(link)
    print(resp.getcode())
    # print(resp.read())
    soup = BeautifulSoup(resp.read(), 'html.parser')
    table = soup.find_all('table')[2]
    tr = table.find('tr')
    for item in table.find_all('tr'):
        print('-------')
        print(item)
    # links = [table for a in tr.find_all()]
    # for item in links:
    #     print('-----')
    #     print(item)
    # tables = soup.find_all('table')
    # print(len(tables))
    # for item in tables:
    # print(item.text)
    # info_table = BeautifulSoup(tables[2], 'html.parser')
    # print(info_table)
    # print(soup.prettify())




if __name__ == "__main__":
    main()
