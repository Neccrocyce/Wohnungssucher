import re
import sys
from abc import abstractmethod

import requests

from core.HtmlDecoder import HtmlDocument
from core.apartment import Apartment
from core.utils import BoolPlus


class WohnungssucherBase:
    url_platform: str | None

    zips_included: list[int] | None
    zips_excluded: list[int]

    places_included: list[str] | None
    places_excluded: list[str]

    rent_cold_min: int
    rent_cold_max: int
    rent_warm_min: int
    rent_warm_max: int

    rooms_min: int
    rooms_max: int

    apartment_size_min: int
    apartment_size_max: int

    floors: list[int]
    energy_efficiency_classes: list[str]

    year_of_construction_min: int
    year_of_construction_max: int

    exchange_apartment: BoolPlus

    default_zip: bool
    default_place: bool
    default_rent_cold: bool
    default_rent_warm: bool
    default_room: bool
    default_apartment_size: bool
    default_floor: bool
    default_energy_efficiency_class: bool
    default_year_of_construction: bool
    default_exchange_apartment: bool

    def __init__(self, config: dict, defaults: dict):
        self.set_configurations(
            url_platform=config['url_platform'],
            zips_included=config['zips_included'],
            zips_excluded=config['zips_excluded'],
            places_included=config['places_included'],
            places_excluded=config['places_excluded'],
            rent_cold_min=config['rent_cold_min'],
            rent_cold_max=config['rent_cold_max'],
            rent_warm_min=config['rent_warm_min'],
            rent_warm_max=config['rent_warm_max'],
            rooms_min=config['rooms_min'],
            rooms_max=config['rooms_max'],
            apartment_size_min=config['apartment_size_min'],
            apartment_size_max=config['apartment_size_max'],
            floors=config['floors'],
            energy_efficiency_classes=config['energy_efficiency_classes'],
            year_of_construction_min=config['year_of_construction_min'],
            year_of_construction_max=config['year_of_construction_max'],
            exchange_apartment=config['exchange_apartment']
        )

        self.set_defaults(
            zip=defaults['zip'],
            place=defaults['place'],
            rent_cold=defaults['rent_cold'],
            rent_warm=defaults['rent_warm'],
            room=defaults['room'],
            apartment_size=defaults['apartment_size'],
            floor=defaults['floor'],
            energy_efficiency_class=defaults['energy_efficiency_class'],
            year_of_construction=defaults['year_of_construction'],
            exchange_apartment=defaults['exchange_apartment']
        )

    def set_configurations(
            self,
            url_platform: str | None = None,
            zips_included: list[int] | None = None,
            zips_excluded: list[int] | None = None,
            places_included: list[str] | None = None,
            places_excluded: list[str] | None = None,
            rent_cold_min: int | None = None,
            rent_cold_max: int | None = None,
            rent_warm_min: int | None = None,
            rent_warm_max: int | None = None,
            rooms_min: int | None = None,
            rooms_max: int | None = None,
            apartment_size_min: int | None = None,
            apartment_size_max: int | None = None,
            floors: list[int] | None = None,
            energy_efficiency_classes: list[str] | None = None,
            year_of_construction_min: int | None = None,
            year_of_construction_max: int | None = None,
            exchange_apartment: BoolPlus | None = None
    ):
        self.url_platform = url_platform
        self.zips_included = zips_included
        self.places_included = places_included
        self.floors = floors
        self.energy_efficiency_classes = energy_efficiency_classes

        if zips_excluded is None:
            self.zips_excluded = []
        else:
            self.zips_excluded = zips_excluded

        if places_excluded is None:
            self.places_excluded = []
        else:
            self.places_excluded = places_excluded

        if rent_cold_min is None:
            self.rent_cold_min = 0
        else:
            self.rent_cold_min = rent_cold_min

        if rent_cold_max is None:
            self.rent_cold_max = sys.maxsize
        else:
            self.rent_cold_max = rent_cold_max

        if rent_warm_min is None:
            self.rent_warm_min = 0
        else:
            self.rent_warm_min = rent_warm_min

        if rent_warm_max is None:
            self.rent_warm_max = sys.maxsize
        else:
            self.rent_warm_max = rent_warm_max

        if rooms_min is None:
            self.rooms_min = 0
        else:
            self.rooms_min = rooms_min

        if rooms_max is None:
            self.rooms_max = sys.maxsize
        else:
            self.rooms_max = rooms_max

        if apartment_size_min is None:
            self.apartment_size_min = 0
        else:
            self.apartment_size_min = apartment_size_min

        if apartment_size_max is None:
            self.apartment_size_max = sys.maxsize
        else:
            self.apartment_size_max = apartment_size_max

        if year_of_construction_min is None:
            self.year_of_construction_min = 0
        else:
            self.year_of_construction_min = year_of_construction_min

        if year_of_construction_max is None:
            self.year_of_construction_max = sys.maxsize
        else:
            self.year_of_construction_max = year_of_construction_max

        if exchange_apartment is None:
            self.exchange_apartment = BoolPlus.maybe()
        else:
            self.exchange_apartment = exchange_apartment

        self.default_zip = False
        self.default_place = False
        self.default_rent_cold = False
        self.default_rent_warm = False
        self.default_room = False
        self.default_apartment_size = False
        self.default_floor = False
        self.default_energy_efficiency_class = False
        self.default_year_of_construction = False
        self.default_exchange_apartment = False

    def set_defaults(
            self,
            zip: bool = False,
            place: bool = False,
            rent_cold: bool = False,
            rent_warm: bool = False,
            room: bool = False,
            apartment_size: bool = False,
            floor: bool = False,
            energy_efficiency_class: bool = False,
            year_of_construction: bool = False,
            exchange_apartment: bool = False,
    ):
        self.default_zip = zip
        self.default_place = place
        self.default_rent_cold = rent_cold
        self.default_rent_warm= rent_warm
        self.default_room = room
        self.default_apartment_size = apartment_size
        self.default_floor = floor
        self.default_energy_efficiency_class = energy_efficiency_class
        self.default_year_of_construction = year_of_construction
        self.default_exchange_apartment = exchange_apartment

    def request_url(self, url) -> HtmlDocument:
        """
        Sends an HTTP GET request and convert the response to an HtmlDocument object
        :param url: url to send an HTTP GET request
        :return: HTMLDocument object containing the pages content
        """
        response = requests.get(self.url_platform)
        content = response.text
        html_document = HtmlDocument(content)
        return html_document

    @abstractmethod
    def request_all_apartments(self) -> list[Apartment]:
        """
        Requests all apartments from the platform, extracts them and return them as Apartment object
        :return: list of all apartments
        """
        pass

    def filter_apartments(self, apartments: list[Apartment]) -> list[Apartment]:
        apartments_filtered = []

        for apartment in apartments:
            if not apartment.check_zip(self.zips_included, self.zips_excluded, self.default_zip):
                continue
            if not apartment.check_place(self.places_included, self.places_excluded, self.default_place):
                continue

            if not apartment.check_rent_cold(self.rent_cold_min, self.rent_cold_max, self.default_rent_cold):
                continue
            if not apartment.check_rent_warm(self.rent_warm_min, self.rent_warm_max, self.default_rent_warm):
                continue

            if not apartment.check_rooms(self.rooms_min, self.rooms_max, self.default_room):
                continue

            if not apartment.check_apartment_size(
                    self.apartment_size_min, self.apartment_size_max, self.default_apartment_size
            ):
                continue

            if not apartment.check_floor(self.floors, self.default_floor):
                continue

            if not apartment.check_energy_efficiency_class(
                    self.energy_efficiency_classes, self.default_energy_efficiency_class
            ):
                continue

            if not apartment.check_year_of_construction(
                    self.year_of_construction_min, self.year_of_construction_max, self.default_year_of_construction
            ):
                continue

            if not apartment.check_exchange_apartment(self.exchange_apartment, self.default_exchange_apartment):
                continue

            apartments_filtered.append(apartment)

        return apartments_filtered

    @staticmethod
    def parse_url(url_current: str, href: str) -> str:
        """
        Parses the url of an href element
        Absolute URL: https://domain/path/to/content -> no change
        Relative URL: /path/to/content -> "Domain of url_current"/path/to/content
                      path/to/content -> url_current/path/to/content
        :param url_current: the url of the webpage where the html content was requested from
        :param href: hyperlink reference inside the html content
        :return:
        """
        if re.findall('^[a-z]*://', href):
            return href
        elif href.startswith('/'):
            domain = re.findall('^[a-z]*://[^/]*', url_current)
            if len(domain) != 1:
                raise ValueError(f'Invalid url {url_current}')
            domain = domain[0]
            return f'{domain}{href}'
        else:
            return f'{url_current}{href}'








