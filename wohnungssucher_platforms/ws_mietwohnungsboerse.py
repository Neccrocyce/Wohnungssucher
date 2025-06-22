import os.path
import re

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

expected_keys_apts_raw = [
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

apartment_portal_name = 'Mietwohnungsboerse'
url = 'https://www.mietwohnungsboerse.de/Immobilien.htm?action_form=search&vermarktungsart=MIETE_PACHT&plz=8%2C9'
filename_savefile_0 = 'mietwohnungsboerse_0.json'
filename_savefile_1 = 'mietwohnungsboerse_1.json'
filename_logfile = 'mietwohnungsboerse_errors.json'

####################
# CLASS DEFINITION #
####################

class WSMietwohnungsboerse(WohnungssucherBase):

    def __init__(self, config, defaults_user):
        path_savefile_0 = os.path.join(config['path_files'], filename_savefile_0)
        path_savefile_1 = os.path.join(config['path_files'], filename_savefile_1)
        path_logfile = os.path.join(config['path_files'], filename_logfile)
        super().__init__(
            config_user=config,
            defaults_0=defaults_0,
            defaults_1=defaults_user,
            platform_name=apartment_portal_name,
            url_platform=url,
            path_savefile_0=path_savefile_0,
            path_savefile_1=path_savefile_1,
            path_logfile=path_logfile,
            exp_keys_apts_raw=expected_keys_apts_raw
        )

    def request_all_apartments_raw(self) -> list[dict]:
        html_full = self.request_url(self.url_platform)
        if html_full is None:
            raise ValueError(f'Request to webpage with url "{self.url_platform}" returned status code different than 200')
        html_apts = html_full.get_element_by_id('immo-container-results')
        if html_apts is None:
            self.log_error_html_content_not_found('id', 'immo-container-results', critical=True)

        apartments_raw = []
        for html_apts_each in html_apts.children:
            # load html of apartment
            apt_raw = {}
            url_part = html_apts_each.children[1].children[0].attributes['href']
            url = self.parse_url(self.url_platform, url_part)
            if url is None:
                self.log_error('fCould not load apartment from url "{url}". Invalid url format. Skipping apartment.')
            html_apt = self.request_url(url)
            if html_apt is None:
                self.log_error(f'Could not load apartment from url "{url}". '
                               f'Status code different than 200. Skipping apartment')
                continue
            apt_raw['url'] = url

            # extract title
            html_apt_title = html_apt.get_elements_by_class('objektTitel h2')
            if len(html_apt_title) != 1:
                self.log_error_html_content_not_found('class', 'objektTitel h2')
            apt_raw['description'] = html_apt_title[0].inner_html

            # extract apartment attributes
            html_apt_attrs = html_apt.get_elements_by_class('objektDatenTabelle')
            if len(html_apt_attrs) != 1:
                self.log_error_html_content_not_found('class', 'objektDatenTabelle')
            html_apt_attrs = html_apt_attrs[0]
            html_apt_attrs_gen = html_apt_attrs.children[0].children[0].children[0]

            apt_raw['id'] = html_apt_attrs_gen.children[0].children[0].children[0].inner_html[11:]

            for html_apt_attrs_gen_i in html_apt_attrs_gen.children[1:]:
                for line in html_apt_attrs_gen_i.children:
                    for cell in line.children:
                        if cell.attributes['class'] == 'clear':
                            continue
                        attr_name = cell.children[0].inner_html
                        attr_value = cell.children[1].inner_html
                        apt_raw[attr_name] = attr_value

            apartments_raw.append(apt_raw)

        return apartments_raw

    # def request_apartment(self, url: str) -> dict:
    #     pass

    def map_apt_keys(self, apts_raw: list[dict]) -> list[dict]:
        apts_dicts = []
        for apt_raw in apts_raw:
            apt_dict = {
                'id': apt_raw['id'],
                'description': apt_raw['description'],
                'url': apt_raw['url'],
                'street': None,
                'house_number': None,
                'rent_cold': apt_raw['Nettokaltmiete'],
                'rent_warm': apt_raw['Warmmiete'],
                'rooms': apt_raw['Zimmeranzahl'],
                'apartment_size': apt_raw['Wohnfläche'],
                'floor': apt_raw['Etage'],
                'year_of_construction': apt_raw['Baujahr'],
                'heating_type': apt_raw['Heizungsart'],
                'energy_efficiency_class': apt_raw['Energieeffizienzklasse'],
                'exchange_apartment': False
            }

            # extract zip code and place
            if apt_raw['Ort'] is None:
                apt_dict['zip'] = None
                apt_dict['place'] = None
            else:
                try:
                    apt_dict['zip'] = apt_raw['Ort'][:5]
                except IndexError:
                    apt_dict['zip'] = None
                    value = apt_raw['Ort']
                    print(f'Warning: Cannot obtain zip code from "{value}"')

                try:
                    place = apt_raw['Ort'][6:]
                    apt_dict['place'] = re.findall('[^ ]*', place)[0]
                except IndexError:
                    apt_dict['place'] = None
                    value = apt_raw['Ort']
                    print(f'Warning: Cannot obtain place from "{value}"')

            # compute warm rent if property "Nebenkosten" instead of "Warmmiete"
            if apt_raw['Warmmiete'] is None and 'Nebenkosten' in apt_raw.keys():
                apt_dict['rent_warm'] = self.compute_warm_rent_from_additional_costs(
                    apt_raw['Nettokaltmiete'], apt_raw['Nebenkosten']
                )

            apts_dicts.append(apt_dict)

        return apts_dicts
