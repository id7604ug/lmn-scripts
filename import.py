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
# (Featuring, Tours, Release Party, etc.) In this case they have to be parsed one by one
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


# Returns the indexes of the canceled shows, which are kept on the page for some reason
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


def get_show_dates():
    url = "http://first-avenue.com/calendar"
    f = urllib.request.urlopen(url)
    soup = BeautifulSoup(f, 'html.parser')
    dates = []
    # All dates and times of shows on the page are in the same class
    for a in soup.find_all("span", class_="date-display-single"):
        dates.append(a.text)

    return dates

# Function to check if artist exists
# Inspired by http://stackoverflow.com/questions/20449048/python-psycopg2-check-row-exists
def artist_exists(name, conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM lmn_artist WHERE name=%s", (name,))
        # Returns true if name was not found
        return cur.fetchone() is not None

# Function to check if venu exists
def venue_exists(venue, conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM lmn_venue WHERE name=%s", (venue[0],))
        # Return true if name was not found
        return cur.fetchone() is not None


def main():
    show_dates = get_show_dates()
    artists = get_artists_firstave()
    venues = get_venues_firstave()
    clean_venues = []

    # A list of non-repeating venues
    for a in range(len(venues)):
        if venues[a] not in clean_venues:
            clean_venues.append(venues[a])

    try:
        conn = psycopg2.connect("dbname=" + os.environ['POSTGRES_LMNOP_DATABASE'] + " user='lmnop' host=" = os.environ['POSTGRES_LMNOP_HOST'] + " password=" + os.environ['POSTGRES_LMNOP_USER_PASSWORD'])
        conn.autocommit = True
        cur = conn.cursor()

        # Add artists to database table lmn_artist
        for x in range(len(artists)):
            if not artist_exists(artists[x], conn):
                SQL = "INSERT INTO lmn_artist (name) VALUES (%s)"
                data = (str(artists[x]),)
                cur.execute(SQL, data)

        print("Artists added successfully")

        # Add venues to database table lmn_venue
        for y in range(len(clean_venues)):
            if not venue_exists(clean_venues[y], conn):
                SQL = "INSERT INTO lmn_venue (name, city, state) VALUES (%s, %s, %s)"
                data = (clean_venues[y][0], clean_venues[y][1], "MN")
                cur.execute(SQL, data)

        print("Venues added successfully")

        # Combine artists & venues to create shows in database table lmn_show
        cur.execute("SELECT id FROM lmn_artist WHERE name=%s", (artists[0],))   # Starting point: artists we just added
        start = cur.fetchone()
        for z in range(len(show_dates)):
            if ("pm" not in show_dates[z]) or ("am" not in show_dates[z]):
                date = show_dates[z]
            else:
                # When we reach else, date is labeled a day and the next value in show_dates is a time, thus date + time
                datetime = date + " " + show_dates[z]
                artistId = start[0] + z
                venueName = venues[z][0]
                cur.execute("SELECT id FROM lmn_venue WHERE name=%s", (venueName,))
                venueId = cur.fetchone()

                SQL = ("INSERT INTO lmn_show (show_date, artist_id, venue_id) VALUES (%s, %s, %s)")
                data = (datetime, artistId, venueId)
                cur.execute(SQL, data)

        print("Shows added successfully.\nImport complete.")

    except Exception as e:
        print("Error: " + str(e))


# Run this once the postgres server is running to add current artists & shows to database
if __name__ == '__main__':
    main()
