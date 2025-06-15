import os.path
import re

from core.apartment import Apartment
from core.wohnungssucher_base import WohnungssucherBase

##################
# DEFAULT VALUES #
##################
"""
default_zip: Always
default_place: Always
default_rent_cold: Always
default_rent_warm: Always
default_room: Always
default_apartment_size: Always
default_floor: Partially
default_energy_efficiency_class: Partially
default_year_of_construction: Always
default_exchange_apartment: No
"""

defaults_0 = {
    'zip': False,
    'place': False,
    'rent_cold': False,
    'rent_warm': False,
    'room': False,
    'apartment_size': False,
    'floor': False,
    'energy_efficiency_class': False,
    'year_of_construction': False,
    'exchange_apartment': False
}

url = 'https://www.mietwohnungsboerse.de/Immobilien.htm?action_form=search&vermarktungsart=MIETE_PACHT&plz=8%2C9'
filename_savefile_0 = 'mietwohnungsboerse_0.json'
filename_savefile_1 = 'mietwohnungsboerse_1.json'

####################
# CLASS DEFINITION #
####################

class WSMietwohnungsboerse(WohnungssucherBase):
    print_msg = True

    def __init__(self, config, defaults_user):
        path_savefile_0 = os.path.join(config['path_files'], filename_savefile_0)
        path_savefile_1 = os.path.join(config['path_files'], filename_savefile_1)
        super().__init__(config, defaults_0, defaults_user, url, path_savefile_0, path_savefile_1)

    def request_all_apartments(self) -> list[Apartment]:
        html_full = self.request_url(self.url_platform)
        if html_full is None:
            raise ValueError('Request to webpage returned status code different than 200')
        html_apts = html_full.get_element_by_id('immo-container-results')
        if html_apts is None:
            self.raise_error_html_content_not_found('id', 'immo-container-results')

        apartments = []
        for html_apts_each in html_apts.children:
            # load html of apartment
            apt_attr_raw = {}
            url_part = html_apts_each.children[1].children[0].attributes['href']
            url = self.parse_url(self.url_platform, url_part)
            html_apt = self.request_url(url)
            if html_apt is None:
                print('Could not load apartment from url. Status code different than 200. Skip apartment')
                continue
            apt_attr_raw['url'] = url

            # extract title
            html_apt_title = html_apt.get_elements_by_class('objektTitel h2')
            if len(html_apt_title) != 1:
                self.raise_error_html_content_not_found('class', 'objektTitel h2')
            apt_attr_raw['Description'] = html_apt_title[0].inner_html

            # extract apartment attributes
            html_apt_attrs = html_apt.get_elements_by_class('objektDatenTabelle')
            if len(html_apt_attrs) != 1:
                self.raise_error_html_content_not_found('class', 'objektDatenTabelle')
            html_apt_attrs = html_apt_attrs[0]
            html_apt_attrs_gen = html_apt_attrs.children[0].children[0].children[0]

            apt_attr_raw['id'] = html_apt_attrs_gen.children[0].children[0].children[0].inner_html[11:]

            for html_apt_attrs_gen_i in html_apt_attrs_gen.children[1:]:
                for line in html_apt_attrs_gen_i.children:
                    for cell in line.children:
                        if cell.attributes['class'] == 'clear':
                            continue
                        attr_name = cell.children[0].inner_html
                        attr_value = cell.children[1].inner_html
                        apt_attr_raw[attr_name] = attr_value

            apartment = self.create_apartment(apt_attr_raw)
            apartments.append(apartment)

        return apartments

    def add_missing_keys(self, apt_attr_raw: dict):
        """
        TODO put in base class
        Checks if apt_attr_raw contains all expected keys and add all missing keys with the value None
        street and house number are ignored since they are never set
        """
        expected_keys = [
            'Nettokaltmiete',
            'Warmmiete',
            'Zimmeranzahl',
            'Wohnfläche',
            'Etage',
            'Baujahr',
            'Heizungsart',
            'Energieeffizienzklasse',
            'Ort'
        ]

        missing_keys = []

        for exp_key in expected_keys:
            if exp_key not in apt_attr_raw.keys():
                apt_attr_raw[exp_key] = None
                missing_keys.append(exp_key)

        if missing_keys:
            apt_id = apt_attr_raw['id']
            self.print_info(
                f'Missing properties for apartment {apt_id}: {missing_keys}. Setting to None.'
            )

    def parse_keys(self, apt_attr_raw: dict):
        """
        Parse the value of all keys in apt_attr_raw to the expected data type.
        If the value cannot be parsed it will be set to None
        """
        try:
            if apt_attr_raw['Ort'] is not None:
                apt_attr_raw['zip'] = int(apt_attr_raw['Ort'][:5])
            else:
                apt_attr_raw['zip'] = None
        except (IndexError, TypeError):
            apt_attr_raw['zip'] = None
            value = apt_attr_raw['Ort']
            print(f'Warning: Cannot parse zip code "{value}"')

        try:
            if apt_attr_raw['Ort'] is not None:
                place = apt_attr_raw['Ort'][6:]
                apt_attr_raw['place'] = re.findall('[^ ]*', place)[0]
            else:
                apt_attr_raw['place'] = None
        except (IndexError, TypeError):
            apt_attr_raw['place'] = None
            value = apt_attr_raw['Ort']
            print(f'Warning: Cannot parse place "{value}"')

        try:
            if apt_attr_raw['Nettokaltmiete'] is not None:
                apt_attr_raw['Nettokaltmiete'] = self.parse_int_from_euro(apt_attr_raw['Nettokaltmiete'])
        except (ValueError, TypeError):
            apt_attr_raw['Nettokaltmiete'] = None
            value = apt_attr_raw['Nettokaltmiete']
            print(f'Warning: Cannot parse Nettokaltmiete "{value}"')

        try: # TODO Nebenkosten
            if apt_attr_raw['Warmmiete'] is not None:
                apt_attr_raw['Warmmiete'] = self.parse_int_from_euro(apt_attr_raw['Warmmiete'])
        except (ValueError, TypeError):
            apt_attr_raw['Warmmiete'] = None
            value = apt_attr_raw['Warmmiete']
            print(f'Warning: Cannot parse Warmmiete "{value}"')

        try:
            if apt_attr_raw['Zimmeranzahl'] is not None:
                apt_attr_raw['Zimmeranzahl'] = float(apt_attr_raw['Zimmeranzahl'].replace(',', '.'))
        except (ValueError, TypeError):
            apt_attr_raw['Zimmeranzahl'] = None
            value = apt_attr_raw['Zimmeranzahl']
            print(f'Warning: Cannot parse Zimmeranzahl "{value}"')

        try:
            if apt_attr_raw['Wohnfläche'] is not None:
                apt_attr_raw['Wohnfläche'] = self.parse_float_from_apt_size(apt_attr_raw['Wohnfläche'])
        except (ValueError, TypeError):
            apt_attr_raw['Wohnfläche'] = None
            value = apt_attr_raw['Wohnfläche']
            print(f'Warning: Cannot parse Wohnfläche "{value}"')

        try:
            if apt_attr_raw['Etage'] is not None:
                apt_attr_raw['Etage'] = int(apt_attr_raw['Etage'])
        except (ValueError, TypeError):
            apt_attr_raw['Etage'] = None
            value = apt_attr_raw['Etage']
            print(f'Warning: Cannot parse Etage "{value}"')

        try:
            if apt_attr_raw['Baujahr'] is not None:
                apt_attr_raw['Baujahr'] = int(apt_attr_raw['Baujahr'])
        except (ValueError, TypeError):
            apt_attr_raw['Baujahr'] = None
            value = apt_attr_raw['Baujahr']
            print(f'Warning: Cannot parse Baujahr "{value}"')

    def create_apartment(self, apt_attr_raw: dict) -> Apartment:
        self.add_missing_keys(apt_attr_raw)
        self.parse_keys(apt_attr_raw)

        apt_dict = {
            'id': apt_attr_raw['id'],
            'description': apt_attr_raw['Description'],
            'url': apt_attr_raw['url'],
            'zip': apt_attr_raw['zip'],
            'place': apt_attr_raw['place'],
            'street': None,
            'house_number': None,
            'rent_cold': apt_attr_raw['Nettokaltmiete'],
            'rent_warm': apt_attr_raw['Warmmiete'],
            'rooms': apt_attr_raw['Zimmeranzahl'],
            'apartment_size': apt_attr_raw['Wohnfläche'],
            'floor': apt_attr_raw['Etage'],
            'year_of_construction': apt_attr_raw['Baujahr'],
            'heating_type': apt_attr_raw['Heizungsart'],
            'energy_efficiency_class': apt_attr_raw['Energieeffizienzklasse'],
            'exchange_apartment': False
        }

        return Apartment.from_dict(apt_dict)

    def print_info(self, info):
        if self.print_msg:
            print(info)
