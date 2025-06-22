import json
import os.path
import re
import sys
from abc import abstractmethod
from datetime import datetime, time

import requests

import utils
from core.HtmlDecoder import HtmlDocument
from core.apartment import Apartment
from core.utils import BoolPlus


class WohnungssucherBase:
    platform_name: str

    url_platform: str | None

    # Path to the savefile storing all apartments with provide information for all properties defined in default_0.
    # These are usually all properties that provided by the platform for an apartment by default.
    path_savefile_0: str

    # Path to the savefile storing all apartments with provide information for all properties defined in default_1.
    # These are usually all properties defined by the user to be important.
    path_savefile_1: str

    # Path to the logfile storing errors that occurred during a run.
    path_logfile: str

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

    email_from_addr: str
    email_to_addr: str | None

    # all expected keys in raw apartment dictionary which is returned by request_all_apartments_raw
    exp_keys_apts_raw: list[str]

    # list all occurred errors which are not critical
    occurred_errors: list[dict]

    def __init__(
            self,
            config_user: dict,
            defaults_0: dict,
            defaults_1: dict,
            platform_name: str,
            url_platform: str,
            path_savefile_0: str,
            path_savefile_1: str,
            path_logfile: str,
            exp_keys_apts_raw: list[str]
    ):
        self.set_configurations(config=config_user)

        self.platform_name = platform_name
        self.url_platform = url_platform
        self.path_savefile_0 = path_savefile_0
        self.path_savefile_1 = path_savefile_1
        self.path_logfile = path_logfile

        self.defaults_0 = defaults_0
        self.defaults_1 = defaults_1

        self.exp_keys_apts_raw = exp_keys_apts_raw

        os.makedirs(os.path.dirname(self.path_savefile_0), exist_ok=True)
        os.makedirs(os.path.dirname(self.path_savefile_1), exist_ok=True)
        os.makedirs(os.path.dirname(self.path_logfile), exist_ok=True)

        self.occurred_errors = []


    def __call__(self, *args, **kwargs):
        apartments = self.request_all_apartments_raw()
        self._add_missing_keys(apartments)
        apartments = self.map_apt_keys(apartments)
        apartments = self._parse_apartments(apartments)

        apts_0 = self._filter_apartments(apartments, self.defaults_0)
        apts_1 = self._filter_apartments(apartments, self.defaults_1)
        apts_1 = self._remove_known_apartments(apts_0, apts_1)

        known_apts_0 = self.load_apartments(self.path_savefile_0)
        known_apts_1 = self.load_apartments(self.path_savefile_1)

        new_apts_0 = self._remove_known_apartments(known_apts_0 + known_apts_1, apts_0)
        new_apts_1 = self._remove_known_apartments(known_apts_0 + known_apts_1, apts_1)

        known_apts_keep_0 = self._remove_old_apartments(known_apts_0)
        known_apts_keep_1 = self._remove_old_apartments(known_apts_1)

        self.save_apartments(self.path_savefile_0, known_apts_keep_0 + new_apts_0)
        self.save_apartments(self.path_savefile_1, known_apts_keep_1 + new_apts_1)

        self._send_mail(new_apts_0, new_apts_1)
        self.save_errors()

        print('\n' + self.platform_name)
        print(f'New apartments: {new_apts_0}')
        print(f'Further apartments: {new_apts_1}')

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

        self.email_from_addr = config['email_from_address']
        self.email_to_addr = config['email_to_address']


    @abstractmethod
    def request_all_apartments_raw(self) -> list[dict]:
        """
        Requests all apartments from the platform, extracts them and return them as dictionary.
        The key-value pairs of the dictionary describe the properties of the apartment.
        The name of the keys can differ from the attribute names of the apartment class.
        Also, not all properties must be given.
        :return: list of all apartments
        """
        pass

    @abstractmethod
    def map_apt_keys(self, apts_raw: list[dict]) -> list[dict]:
        """
        Maps the values in apts_raw to the keys used in the apartment class.
        The keys in the resulting dictionaries must be equal to the attributes names of the class apartment.
        However, the datatypes can be arbitrary.
        :param apts_raw: list of dictionaries where each dictionary represents one apartment
        :return: list of dictionaries where each dictionary represents one apartment.
            The keys in the dictionary must be equal to the attributes names of the class apartment.
        """
        pass

    def _add_missing_keys(self, apts_raw: list[dict]):
        """
        Checks if each apartment of apts_raw contains all expected keys and add all missing keys with the value None
        street and house number are ignored since they are never set
        """

        for apt_raw in apts_raw:
            missing_keys = []

            for exp_key in self.exp_keys_apts_raw:
                if exp_key not in apt_raw.keys():
                    apt_raw[exp_key] = None
                    missing_keys.append(exp_key)

            if missing_keys:
                apt_id = apt_raw['id']
                print(f'Missing properties for apartment {apt_id}: {missing_keys}. Setting to None.')

    def _parse_apartments(self, apts_dicts: list[dict]) -> list[Apartment]:
        """
        Parse the value of all keys in apt_attr_raw to the expected data type.
        If the value cannot be parsed it will be set to None
        """
        apts = []
        for apt_dict in apts_dicts:
            try:
                if apt_dict['zip'] is not None:
                    apt_dict['zip'] = int(apt_dict['zip'])
            except (ValueError, TypeError):
                apt_dict['zip'] = None
                value = apt_dict['zip']
                self.log_error(f'Error: Cannot parse zip code "{value}"')

            try:
                if apt_dict['house_number'] is not None:
                    apt_dict['house_number'] = int(apt_dict['house_number'])
            except (ValueError, TypeError):
                apt_dict['house_number'] = None
                value = apt_dict['house_number']
                self.log_error(f'Error: Cannot parse house_number "{value}"')

            try:
                if apt_dict['rent_cold'] is not None:
                    apt_dict['rent_cold'] = self.parse_int_from_euro(apt_dict['rent_cold'])
            except (ValueError, TypeError):
                apt_dict['rent_cold'] = None
                value = apt_dict['rent_cold']
                self.log_error(f'Error: Cannot parse rent_cold "{value}"')

            try:
                if apt_dict['rent_warm'] is not None:
                    apt_dict['rent_warm'] = self.parse_int_from_euro(apt_dict['rent_warm'])
            except (ValueError, TypeError):
                apt_dict['rent_warm'] = None
                value = apt_dict['rent_warm']
                self.log_error(f'Error: Cannot parse rent_warm "{value}"')

            try:
                if apt_dict['rooms'] is not None:
                    apt_dict['rooms'] = float(apt_dict['rooms'].replace(',', '.'))
            except (ValueError, TypeError):
                apt_dict['rooms'] = None
                value = apt_dict['rooms']
                self.log_error(f'Error: Cannot parse number of rooms "{value}"')

            try:
                if apt_dict['apartment_size'] is not None:
                    apt_dict['apartment_size'] = self.parse_float_from_apt_size(apt_dict['apartment_size'])
            except (ValueError, TypeError):
                apt_dict['apartment_size'] = None
                value = apt_dict['apartment_size']
                self.log_error(f'Error: Cannot parse apartment_size "{value}"')

            try:
                if apt_dict['floor'] is not None:
                    apt_dict['floor'] = int(apt_dict['floor'])
            except (ValueError, TypeError):
                apt_dict['floor'] = None
                value = apt_dict['floor']
                self.log_error(f'Error: Cannot parse floor "{value}"')

            try:
                if apt_dict['year_of_construction'] is not None:
                    apt_dict['year_of_construction'] = int(apt_dict['year_of_construction'])
            except (ValueError, TypeError):
                apt_dict['year_of_construction'] = None
                value = apt_dict['year_of_construction']
                self.log_error(f'Error: Cannot parse year_of_construction "{value}"')

            # TODO parse exchange_apartment

            apts.append(Apartment.from_dict(apt_dict))

        return apts


    def _filter_apartments(self, apartments: list[Apartment], defaults: dict) -> list[Apartment]:
        """
        Removes all apartment that do not match the defined requirements.
        If a value is set to None the corresponding default value decides whether the apartment is kept or not
        (True: keep, False: discard)
        :param apartments:
        :param defaults:
        :return:
        """
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
    def _remove_known_apartments(known_apartments: list[Apartment], all_apartments: list[Apartment]) -> list[Apartment]:
        """
        Removes all known apartments from the list of all_apartments to keep only unknown apartments
        :param known_apartments: list of known apartments
        :param all_apartments: list of all found apartments
        :return: All apartments that are not listed in "known_apartments"
        """
        new_apts = [x for x in all_apartments if x.id not in {y.id for y in known_apartments}]
        return new_apts

    def _send_mail(self, apartments_0: list[Apartment], apartments_1: list[Apartment]):
        """
        Sends an email with all given apartments
        :param apartments_0:
        :param apartments_1:
        :return:
        """
        if self.email_to_addr is None:
            return

        if len(apartments_0) == 0:
            headline_0 = ''
        elif len(apartments_0) == 1:
            headline_0 = '1 neues Angebot'
        else:
            headline_0 = f'{len(apartments_0)} neue Angebote'
        email_content = '<!DOCTYPE html>\n<html lang="en">\n'
        email_content += Apartment.get_html_header()
        email_content += f'\n<body>\n\t<div>\n\t\t<h1>{headline_0}</h1>\n\t</div>\n'
        for apt_0 in apartments_0:
            email_content += apt_0.to_html()[1]

        if apartments_1:
            email_content += '\n\t<div>\n\t\t<h1>Weitere Angebote</h1>\n\t</div>\n'
            for apt_1 in apartments_1:
                email_content += apt_1.to_html()[1]
        email_content += '</body>\n</html>'

        subject = f'Neue Wohnungen bei {self.platform_name}'

        utils.send_mail(self.email_from_addr, self.email_to_addr, subject, msg_html=email_content)

    def load_errors(self) -> list[dict]:
        """
        Loads saved errors from a json file
        :return: list of errors
        """
        if not os.path.exists(self.path_logfile):
            return []

        with open(self.path_logfile, 'r') as file:
            errors = json.load(file)

        return errors

    def save_errors(self):
        errors_all = self.load_errors()
        errors_all += self.occurred_errors

        with open(self.path_logfile, 'w') as f:
            json.dump(errors_all, f)

    def _remove_old_apartments(self, apartments: list[Apartment]) -> list[Apartment]:
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

    def parse_url(self, url_current: str, href: str) -> str | None:
        """
        Parses the url of an href element
        Absolute URL: https://domain/path/to/content -> no change
        Relative URL: /path/to/content -> "Domain of url_current"/path/to/content
                      path/to/content -> url_current/path/to/content
        :param url_current: the url of the webpage where the html content was requested from
        :param href: hyperlink reference inside the html content
        :return: the complete url or None if url_current is invalid
        """
        if re.findall('^[a-z]*://', href):
            return href
        elif href.startswith('/'):
            domain = re.findall('^[a-z]*://[^/]*', url_current)
            if len(domain) != 1:
                self.log_error(f'Invalid url format "{url_current}"')
                return None
            domain = domain[0]
            return f'{domain}{href}'
        else:
            return f'{url_current}{href}'

    @staticmethod
    def parse_int_from_euro(number: str | int) -> int:
        if isinstance(number, int):
            return number
        try:
            number = re.sub('[€ .]', '', number)
            number = re.sub('[,]', '.', number)
            return int(float(number))
        except:
            raise TypeError

    @staticmethod
    def parse_float_from_apt_size(apt_size: str | float) -> float:
        if isinstance(apt_size, float):
            return apt_size
        try:
            apt_size_float = re.findall('[\d.,]+', apt_size)[0]
            apt_size_float = float(apt_size_float.replace(',', '.'))
            return apt_size_float
        except:
            raise TypeError

    def compute_warm_rent_from_additional_costs(self, rent_cold: int | str, additional_costs: int | str):
        if isinstance(rent_cold, str):
            rent_cold = self.parse_int_from_euro(rent_cold)
        if isinstance(additional_costs, str):
            additional_costs = self.parse_int_from_euro(additional_costs)

        return rent_cold + additional_costs

    def log_error(self, msg: str, critical: bool = False):
        self.occurred_errors.append({
            'timestamp': datetime.now().timestamp(),
            'type': 'CRITICAL' if critical else 'ERROR',
            'msg': msg
        })

        print(msg, file=sys.stderr)


    def log_error_html_content_not_found(self, content_type: str, content: str, critical: bool = False):
        err_msg = (f'None or multiple instances of {content_type} "{content}" in response. '
                   f'Expected exactly one instance. Maybe webpage has been modified?')
        if critical:
            raise ValueError(err_msg)
        else:
            err_msg += ' Skipped apartment!'
            self.log_error(err_msg)






