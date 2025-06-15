import json
import os.path
import re
import sys
from abc import abstractmethod
from datetime import datetime, time

import requests

from core.HtmlDecoder import HtmlDocument
from core.apartment import Apartment
from core.utils import BoolPlus


class WohnungssucherBase:
    url_platform: str | None

    # Path to the savefile storing all apartments with provide information for all properties defined in default_0.
    # These are usually all properties that provided by the platform for an apartment by default.
    path_savefile_0: str

    # Path to the savefile storing all apartments with provide information for all properties defined in default_1.
    # These are usually all properties defined by the user to be important.
    path_savefile_1: str

    # Defines which properties must be provided for an apartment to be considered in group 0.
    # Group 0 usually contains all apartments for that all properties are provided by the platform.
    defaults_0: dict

    # Defines which properties must be provided for an apartment to be considered in group 1.
    # Group 1 usually contains all apartments containing at least all properties defined in the user settings.
    defaults_1: dict

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

    max_apartment_age: int | None



    def __init__(
            self,
            config_user: dict,
            defaults_0: dict,
            defaults_1: dict,
            url_platform: str,
            path_savefile_0: str,
            path_savefile_1: str
    ):
        self.set_configurations(config=config_user)

        self.url_platform = url_platform
        self.path_savefile_0 = path_savefile_0
        self.path_savefile_1 = path_savefile_1

        self.defaults_0 = defaults_0
        self.defaults_1 = defaults_1

        os.makedirs(os.path.dirname(self.path_savefile_0), exist_ok=True)
        os.makedirs(os.path.dirname(self.path_savefile_1), exist_ok=True)


    def __call__(self, *args, **kwargs):
        apartments = self.request_all_apartments()

        apts_0 = self.filter_apartments(apartments, self.defaults_0)
        apts_1 = self.filter_apartments(apartments, self.defaults_1)
        apts_1 = self.remove_known_apartments(apts_0, apts_1)

        known_apts_0 = self.load_apartments(self.path_savefile_0)
        known_apts_1 = self.load_apartments(self.path_savefile_1)

        new_apts_0 = self.remove_known_apartments(known_apts_0 + known_apts_1, apts_0)
        new_apts_1 = self.remove_known_apartments(known_apts_0 + known_apts_1, apts_1)

        known_apts_keep_0 = self.remove_old_apartments(known_apts_0)
        known_apts_keep_1 = self.remove_old_apartments(known_apts_1)

        self.save_apartments(self.path_savefile_0, known_apts_keep_0 + new_apts_0)
        self.save_apartments(self.path_savefile_1, known_apts_keep_1 + new_apts_1)

        self.send_mail(new_apts_0, new_apts_1)

    def set_configurations(self, config: dict):
        self.zips_included = config['zips_included']
        self.places_included = config['places_included']
        self.floors = config['floors']
        self.energy_efficiency_classes = config['energy_efficiency_classes']
        self.max_apartment_age = config['max_apartment_age']

        if config['zips_excluded'] is None:
            self.zips_excluded = []
        else:
            self.zips_excluded = config['zips_excluded']

        if config['places_excluded'] is None:
            self.places_excluded = []
        else:
            self.places_excluded = config['places_excluded']

        if config['rent_cold_min'] is None:
            self.rent_cold_min = 0
        else:
            self.rent_cold_min = config['rent_cold_min']

        if config['rent_cold_max'] is None:
            self.rent_cold_max = sys.maxsize
        else:
            self.rent_cold_max = config['rent_cold_max']

        if config['rent_warm_min'] is None:
            self.rent_warm_min = 0
        else:
            self.rent_warm_min = config['rent_warm_min']

        if config['rent_warm_max'] is None:
            self.rent_warm_max = sys.maxsize
        else:
            self.rent_warm_max = config['rent_warm_max']

        if config['rooms_min'] is None:
            self.rooms_min = 0
        else:
            self.rooms_min = config['rooms_min']

        if config['rooms_max'] is None:
            self.rooms_max = sys.maxsize
        else:
            self.rooms_max = config['rooms_max']

        if config['apartment_size_min'] is None:
            self.apartment_size_min = 0
        else:
            self.apartment_size_min = config['apartment_size_min']

        if config['apartment_size_max'] is None:
            self.apartment_size_max = sys.maxsize
        else:
            self.apartment_size_max = config['apartment_size_max']

        if config['year_of_construction_min'] is None:
            self.year_of_construction_min = 0
        else:
            self.year_of_construction_min = config['year_of_construction_min']

        if config['year_of_construction_max'] is None:
            self.year_of_construction_max = sys.maxsize
        else:
            self.year_of_construction_max = config['year_of_construction_max']

        if config['exchange_apartment'] is None:
            self.exchange_apartment = BoolPlus.maybe()
        else:
            self.exchange_apartment = config['exchange_apartment']


    @abstractmethod
    def request_all_apartments(self) -> list[Apartment]:
        """
        Requests all apartments from the platform, extracts them and return them as Apartment object
        :return: list of all apartments
        """
        pass

    def filter_apartments(self, apartments: list[Apartment], defaults: dict) -> list[Apartment]:
        apartments_filtered = []

        for apartment in apartments:
            if not apartment.check_zip(self.zips_included, self.zips_excluded, defaults['zip']):
                continue
            if not apartment.check_place(self.places_included, self.places_excluded, defaults['place']):
                continue

            if not apartment.check_rent_cold(self.rent_cold_min, self.rent_cold_max, defaults['rent_cold']):
                continue
            if not apartment.check_rent_warm(self.rent_warm_min, self.rent_warm_max, defaults['rent_warm']):
                continue

            if not apartment.check_rooms(self.rooms_min, self.rooms_max, defaults['room']):
                continue

            if not apartment.check_apartment_size(
                    self.apartment_size_min, self.apartment_size_max, defaults['apartment_size']
            ):
                continue

            if not apartment.check_floor(self.floors, defaults['floor']):
                continue

            if not apartment.check_energy_efficiency_class(
                    self.energy_efficiency_classes, defaults['energy_efficiency_class']
            ):
                continue

            if not apartment.check_year_of_construction(
                    self.year_of_construction_min, self.year_of_construction_max, defaults['year_of_construction']
            ):
                continue

            if not apartment.check_exchange_apartment(self.exchange_apartment, defaults['exchange_apartment']):
                continue

            apartments_filtered.append(apartment)

        return apartments_filtered

    @staticmethod
    def load_apartments(filename: str) -> list[Apartment]:
        """
        Loads saved apartments from a json file
        :param filename: path to the json file to be loaded
        :return: list of loaded apartments
        """
        if not os.path.exists(filename):
            return []

        with open(filename, 'r') as file:
            apts_json = json.load(file)

        apartments = []
        for apt in apts_json:
            apartments.append(Apartment.from_dict(apt))

        return apartments

    @staticmethod
    def save_apartments(filename: str, apartments: list[Apartment]):
        """
        Saves all given apartments to a file. The apartments are stored in json format.
        :param filename: path to the json file
        :param apartments: list of all apartments to be saved
        """
        apts_json = []
        for apt in apartments:
            apts_json.append(apt.to_dict())

        with open(filename, 'w') as f:
            json.dump(apts_json, f)

    @staticmethod
    def remove_known_apartments(known_apartments: list[Apartment], all_apartments: list[Apartment]) -> list[Apartment]:
        """
        Removes all known apartments from the list of all_apartments to keep only unknown apartments
        :param known_apartments: list of known apartments
        :param all_apartments: list of all found apartments
        :return: All apartments that are not listed in "known_apartments"
        """
        new_apts = [x for x in all_apartments if x.id not in {y.id for y in known_apartments}]
        return new_apts

    def send_mail(self, apartments_0: list[Apartment], apartments_1: list[Apartment]):
        """
        Sends an email with all given apartments
        :param apartments_0:
        :param apartments_1:
        :return:
        """
        print(apartments_0)
        print(apartments_1)

    def remove_old_apartments(self, apartments: list[Apartment]) -> list[Apartment]:
        """
        Removes all apartments where the release date is older than self.max_apartment_age dqys
        :param apartments: list of apartments to be considered
        :return: list of apartments where their release date is younger.
        """
        if self.max_apartment_age is None:
            return apartments

        current_day = datetime.now().date()
        timestamp_today = datetime.combine(current_day, time(0, 0)).timestamp()
        timestamp_max_age = timestamp_today - 86400 * self.max_apartment_age

        apartments_keep = []
        for apt in apartments:
            if apt.released >= timestamp_max_age:
                apartments_keep.append(apt)

        return apartments_keep

    @staticmethod
    def request_url(url) -> HtmlDocument | None:
        """
        Sends an HTTP GET request and convert the response to an HtmlDocument object
        :param url: url to send an HTTP GET request
        :return: HTMLDocument object containing the pages content
        """
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Request to {url} returned status code {response.status_code}", file=sys.stderr)
            return None
        content = response.text
        html_document = HtmlDocument(content)
        return html_document

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

    @staticmethod
    def parse_int_from_euro(number: str) -> int:
        try:
            number = re.sub('[€ .]', '', number)
            number = re.sub('[,]', '.', number)
            return int(float(number))
        except:
            raise TypeError

    @staticmethod
    def parse_float_from_apt_size(apt_size: str) -> float:
        try:
            apt_size_float = re.findall('[\d.,]+', apt_size)[0]
            apt_size_float = float(apt_size_float.replace(',', '.'))
            return apt_size_float
        except:
            raise TypeError

    @staticmethod
    def raise_error_html_content_not_found(content_type: str, content: str):
        raise ValueError(f'None or multiple instances of {content_type} "{content}" in response. '
                         f'Expected exactly one instance. Maybe webpage has been modified?')








