from codecs import open
from bs4 import BeautifulSoup
from json import dumps
from datetime import datetime


class BachtrackLeecher:
    def __init__(self):
        self.current_listing_soup = None

    def get_title(self):
        return self.current_listing_soup.find("h1", attrs={'id': 'title-section-title'}).contents[0]

    def get_place(self):
        place = self.current_listing_soup.find('span', attrs={'itemtype': 'http://schema.org/Place'})
        name = place.find('span', attrs={'itemprop': 'name'}).text
        address = place.find('span', attrs={'itemtype': 'http://schema.org/Postaladdress'})
        street = address.find('span', attrs={'itemprop': 'streetAddress'})
        street = street.text if street else None
        locality = address.find('a', attrs={'class': 'addressLocality'}).text
        region = address.find('span', attrs={'itemprop': 'addressRegion'}).text
        postalCode = address.find('span', attrs={'itemprop': 'postalCode'}).text
        country = address.find('a', attrs={'itemprop': 'addressCountry'}).text
        gps = place.find('div', attrs={'itemtype': 'http://schema.org/GeoCoordinates'})
        latitude = float(gps.find('meta', attrs={'itemprop': 'latitude'})['content'])
        longitude = float(gps.find('meta', attrs={'itemprop': 'longitude'})['content'])
        return {
            "name": name,
            "street": street,
            "locality": locality,
            "region": region,
            "country": country,
            "postalCode": postalCode,
            "latitude": latitude,
            "longitude": longitude
        }

    def get_date(self):
        date_annotation = self.current_listing_soup.find('div', attrs={'class': 'listing-main-date'}).text
        date = self.current_listing_soup.find('span', attrs={'itemprop': 'startDate'}).text
        multiple_dates = self.current_listing_soup.find('a', attrs={'data-dates': True})
        if multiple_dates:
            multiple_dates = [datetime.utcfromtimestamp(float(item)).isoformat() for item in multiple_dates['data-dates'].split(',')]
        return {
            "date": date,
            "annotation": date_annotation,
            "multiple_dates": multiple_dates
        }

    def get_programme(self):
        programme_table = self.current_listing_soup.find('table', attrs={'id': 'table_listing-programme'})
        programme = []
        for tr in programme_table.findAll('tr'):
            cells = tr.findChildren('td', recursive=False)
            person = cells[0].text
            work = cells[1].text
            note = cells[2].text
            programme.append(
                {
                    "person": person,
                    "work": work,
                    "note": note
                }
            )
        return programme

    def get_performers(self):
        performers_table = self.current_listing_soup.find('table', attrs={'id': 'table_listing-personnel'})
        performers = []
        for tr in performers_table.findAll('tr'):
            cells = tr.findChildren('td', recursive=False)
            person = cells[0].text
            function = cells[1].text
            character = cells[2].text if len(cells) > 2 else None
            note = cells[3].text if len(cells) > 3 else None
            performers.append(
                {
                    "person": person,
                    "function": function,
                    "character": character,
                    "note": note
                }
            )
        return performers

    def leech_listing(self, listing_id):
        with open(listing_id, "r", "utf-*") as f:
            html = f.read()
        self.current_listing_soup = BeautifulSoup(html, 'html.parser')
        title = self.get_title()
        place = self.get_place()
        date = self.get_date()
        programme = self.get_programme()
        performers = self.get_performers()
        data = {
            "title": title,
            "place": place,
            "date": date,
            "programme": programme,
            "performers": performers
        }
        print(dumps(data, indent=2))


def main():
    btl = BachtrackLeecher()
    btl.leech_listing("testlisting.html")
    btl.leech_listing("testlisting2.html")


if __name__ == "__main__":
    main()
