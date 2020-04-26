from codecs import open
from bs4 import BeautifulSoup
from json import dumps, load, dump
from datetime import datetime
from requests import get
from time import sleep


class BachtrackLeecher:
    def __init__(self):
        self.current_listing_soup = None
        try:
            with open("leech.json", "r", "utf-8") as f:
                self.list = load(f)
        except IOError:
            self.list = []

    def persist(self):
        with open("leech.json", "w", "utf-8") as f:
            dump(self.list, f, indent=2)

    def get_last_listing_id(self):
        ids = [item['bachtrack_id'] for item in self.list]
        if len(ids) > 0:
            return max(ids)
        else:
            return 307806

    def get_title(self):
        return self.current_listing_soup.find("h1", attrs={'id': 'title-section-title'}).text

    def get_place(self):
        place = self.current_listing_soup.find('span', attrs={'itemtype': 'http://schema.org/Place'})
        name = place.find('span', attrs={'itemprop': 'name'}).text
        address = place.find('span', attrs={'itemtype': 'http://schema.org/Postaladdress'})
        street = address.find('span', attrs={'itemprop': 'streetAddress'})
        street = street.text if street else None
        locality = address.find('a', attrs={'class': 'addressLocality'}).text
        region = address.find('span', attrs={'itemprop': 'addressRegion'})
        region = region.text if region else None
        postalCode = address.find('span', attrs={'itemprop': 'postalCode'})
        postalCode = postalCode.text if postalCode else None
        country = address.find('a', attrs={'itemprop': 'addressCountry'}).text
        gps = place.find('div', attrs={'itemtype': 'http://schema.org/GeoCoordinates'})
        latitude = gps.find('meta', attrs={'itemprop': 'latitude'})['content']
        latitude = float(latitude) if "." in latitude else None
        longitude = gps.find('meta', attrs={'itemprop': 'longitude'})['content']
        longitude = float(longitude) if "." in longitude else None
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
        if programme_table:
            for tr in programme_table.findAll('tr'):
                cells = tr.findChildren('td', recursive=False)
                person = cells[0].text
                work = cells[1].text
                note = cells[2].text
                programme.append(
                    {
                        "creator": person,
                        "work": work,
                        "note": note
                    }
                )
        return programme

    def get_performers(self):
        performers_table = self.current_listing_soup.find('table', attrs={'id': 'table_listing-personnel'})
        performers = []
        if performers_table:
            for tr in performers_table.findAll('tr'):
                cells = tr.findChildren('td', recursive=False)
                person = cells[0].text
                function = cells[1].text
                character = cells[2].text if len(cells) > 2 else None
                note = cells[3].text if len(cells) > 3 else None
                performers.append(
                    {
                        "performer": person,
                        "function": function,
                        "character": character,
                        "note": note
                    }
                )
        return performers

    def leech_listing(self, listing_id):
        base_url = "https://bachtrack.com/22/291/render/"
        sleep(5.0)
        print("working on", base_url + str(listing_id))
        r = get(base_url + str(listing_id))
        if r.status_code == 200:
            html = r.text
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
                "performers": performers,
                "bachtrack_id": listing_id
            }
            print(dumps(data, indent=2))
            self.list.append(data)
        else:
            print(r.status_code)


def main():
    btl = BachtrackLeecher()
    #next_up = btl.get_last_listing_id() + 1
    next_up = 309239
    for i in range(next_up, 310000, 1):
        btl.leech_listing(i)
        btl.persist()


if __name__ == "__main__":
    main()
