import psycopg2
import os
import urllib
import urllib.request
from bs4 import BeautifulSoup


# This script gets concert information from minneappolisconcerts.net
def mplsconcerts():
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


# Returns a list of all artists on First Avenue's calendar
# TODO artists are tricky- sometimes they have extra information that can't be reliably parsed out
# (Featuring, Tours, Release Party, etc.) In this case they have to be parsed out one by one (sorry)
def get_artists_firstave():
    url = "http://first-avenue.com/calendar"
    f = urllib.request.urlopen(url)
    soup = BeautifulSoup(f, 'html.parser')
    artists = []
    # All shows on that page
    for a in soup.find_all("div", class_="view-content"):
        # Name of each artist
        for b in a.find_all("h2", class_="node-title"):
            # Don't add artist if the show is canceled
            if "CANCELED" not in b.text:
                artists.append(b.text.title())
    return artists


# Returns the indexes of the canceled shows, which are kept on the page for some odd reason
def get_canceled_firstave():
    url = "http://first-avenue.com/calendar"
    f = urllib.request.urlopen(url)
    soup = BeautifulSoup(f, 'html.parser')
    shows = []
    num = 0
    for a in soup.find_all("div", class_="view-content"):
        for b in a.find_all("h2", class_="node-title"):
            if "CANCELED" in b.text:
                shows.append(num)
            num += 1
    return shows


# Returns a list of venues each artist is performing at (each venue is a list of name, city, state)
def get_venues_firstave():
    url = "http://first-avenue.com/calendar"
    f = urllib.request.urlopen(url)
    soup = BeautifulSoup(f, 'html.parser')
    venues = []
    counter = 0
    index = 0
    canceled = get_canceled_firstave()
    # All shows on that page
    for a in soup.find_all("div", class_="view-content"):
        # All links within shows
        for c in a.find_all("a", href=True):
            # Grab the link if it's a link to a venue
            if "/venue/" in c["href"]:
                if index not in canceled:
                    venue_info = []
                    venue_info.append(c.text)
                    # Turf Club & Palace Theatre are in St Paul, the rest are in Minneapolis
                    if c.text in ["Turf Club", "Palace Theatre"]:
                        venue_info.append("St. Paul")
                    else:
                        venue_info.append("Minneapolis")
                    venues.append(venue_info)
                index += 1
            counter += 1
    return venues


def main():
    # lmn_artist: id, name
    # lmn_venue: id, name, city, state
    artists = get_artists_firstave()
    venues = get_venues_firstave()

    try:
        conn = psycopg2.connect("dbname='lmnop' user='lmnop' host='localhost' password=" + os.environ['POSTGRES_LMNOP_USER_PASSWORD'])
        conn.autocommit = True
        cur = conn.cursor()

        # for x in range(len(artists)):
        #     cur.execute("INSERT INTO lmn_artist (name) VALUES (%s)", (artists[x],))
        # print("Artists added successfully")

        for y in range(len(venues)):
            cur.execute("SELECT name FROM lmn_venue WHERE name=%s", (venues[y][0],))
            # TODO should work but gives error
            if cur.fetchOne() is not None:
                SQL = "INSERT INTO lmn_venue (name, city, state) VALUES (%s, %s, %s)"
                data = (venues[y][0], venues[y][1], "MN")
                cur.execute(SQL, data)
        print("Venues added successfully")

    except Exception as e:
        print("Error: " + str(e))


if __name__ == '__main__':
    main()