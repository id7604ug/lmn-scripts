import urllib
import urllib.request
from bs4 import BeautifulSoup


# Returns a list of all artists on First Avenue's calendar
# TODO artists are tricky- sometimes they have extra information that can't be reliably parsed out
# TODO (Featuring, Tours, Release Party, etc.) In this case they have to be parsed out one by one (sorry)
def get_artists():
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
def get_canceled():
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


# Returns a list of venues each artist is performing at
# (Turf Club & Palace Theater are in St Paul, the rest are in Minneapolis)
def get_venues():
    url = "http://first-avenue.com/calendar"
    f = urllib.request.urlopen(url)
    soup = BeautifulSoup(f, 'html.parser')
    venues = []
    counter = 0
    index = 0
    canceled = get_canceled()
    # All shows on that page
    for a in soup.find_all("div", class_="view-content"):
        for c in a.find_all("a", href=True):
            if "/venue/" in c["href"]:
                if index not in canceled:
                    venues.append(c.text)
                index += 1
            counter += 1
    return venues
