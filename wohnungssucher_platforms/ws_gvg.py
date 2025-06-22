

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
default_floor: Always
default_energy_efficiency_class: Always
default_year_of_construction: Always
default_exchange_apartment: No
"""
import os
import re

from wohnungssucher_base import WohnungssucherBase

defaults_ws = {
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
    'description',
    'street_and_number',
    'zip_and_place',
    'rent_cold',
    'rent_warm',
    'rooms',
    'apartment_size',
    'floor',
    'year_of_construction',
    'heating_type',
    'energy_efficiency_class',
]

apartment_portal_name = 'GVG'
url = 'https://www.gvgnet.de/mietobjekte/wohnobjekte/'
filename_savefile_0 = 'gvg_0.json'
filename_savefile_1 = 'gvg_1.json'
filename_logfile = 'gvg_errors.json'


####################
# CLASS DEFINITION #
####################
class WSGVG(WohnungssucherBase):

    def __init__(self, config):
        path_savefile_0 = os.path.join(config['path_files'], filename_savefile_0)
        path_savefile_1 = os.path.join(config['path_files'], filename_savefile_1)
        path_logfile = os.path.join(config['path_files'], filename_logfile)
        super().__init__(
            config_user=config,
            defaults_ws=defaults_ws,
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

        html_apts = html_full.get_elements_by_class('elementor-button elementor-button-link elementor-size-xs')

        apartments_raw = []
        for html_apts_each in html_apts:
            url_apt = html_apts_each.attributes['href']
            if not url_apt.startswith('https://www.gvgnet.de/mietobjekte'):
                continue
            apt_raw = self.request_apartment(url_apt)

            if apt_raw is not None:
                apartments_raw.append(apt_raw)

        return apartments_raw

    def request_apartment(self, url: str) -> dict | None:
        # load html of apartment
        apt_raw = {}

        if url is None:
            self.log_error(f'Could not load apartment from url "{url}". Invalid url format. Skipping apartment.')

        html_apt = self.request_url(url)
        if html_apt is None:
            self.log_error(f'Could not load apartment from url "{url}". '
                           f'Status code different than 200. Skipping apartment')
            return None
        apt_raw['url'] = url

        # extract id
        apt_id = re.findall('mietobjekte/[^/]*', url)
        if len(apt_id) != 1:
            self.log_error(f'Could not find apartment id in url {url}. Maybe url format has changed? Skipping apartment')
            return None
        apt_raw['id'] = apt_id[0][12:]

        # extract description
        search_class = 'product_title entry-title elementor-heading-title elementor-size-default'
        html_apt_prop = html_apt.get_elements_by_class(search_class)
        if len(html_apt_prop) != 1:
            self.log_error_html_content_not_found('class', search_class, add_skip_apartment=True)
            return None
        apt_raw['description'] = html_apt_prop[0].inner_html

        # extract street and house number
        search_class = 'elementor-element elementor-element-1c9a859 elementor-widget elementor-widget-text-editor'
        html_apt_prop = html_apt.get_elements_by_class(search_class)
        if len(html_apt_prop) != 1:
            self.log_error_html_content_not_found('class', search_class)
        apt_raw['street_and_number'] = html_apt_prop[0].children[0].inner_html

        # extract zip code and place
        search_class = 'elementor-element elementor-element-16aff7c elementor-widget elementor-widget-text-editor'
        html_apt_prop = html_apt.get_elements_by_class(search_class)
        if len(html_apt_prop) != 1:
            self.log_error_html_content_not_found('class', search_class)
        apt_raw['zip_and_place'] = html_apt_prop[0].children[0].inner_html

        search_classes = [
            ('Wohnungsdaten', 'elementor-column elementor-col-50 elementor-top-column elementor-element elementor-element-6f1f498'),
            ('Ausstattung', 'elementor-column elementor-col-50 elementor-top-column elementor-element elementor-element-809c26a'),
            ('Mietzinskonditionen', 'elementor-column elementor-col-50 elementor-top-column elementor-element elementor-element-813e0f8'),
            ('Energieausweis', 'elementor-column elementor-col-50 elementor-top-column elementor-element elementor-element-87e5af8')
        ]
        html_blocks = {}

        for name, search_class in search_classes:
            html_block = html_apt.get_elements_by_class(search_class)
            if len(html_block) != 1:
                self.log_error_html_content_not_found('class', search_class, add_skip_apartment=True)
                return None
            html_blocks[name] = html_block[0]


        # extract properties
        class_prop_pair = [
            ('jet-table__cell elementor-repeater-item-4dd1506 jet-table__body-cell', 'year_of_construction', 'Wohnungsdaten'),
            ('jet-table__cell elementor-repeater-item-56fcc5e jet-table__body-cell', 'floor', 'Wohnungsdaten'),
            ('jet-table__cell elementor-repeater-item-c022fe0 jet-table__body-cell', 'rooms', 'Wohnungsdaten'),
            ('jet-table__cell elementor-repeater-item-ae16281 jet-table__body-cell', 'apartment_size', 'Wohnungsdaten'),
            ('jet-table__cell elementor-repeater-item-8ea9b9b jet-table__body-cell', 'rent_cold', 'Mietzinskonditionen'),
            ('jet-table__cell elementor-repeater-item-0ee1239 jet-table__body-cell', 'rent_warm', 'Mietzinskonditionen'),
            ('jet-table__cell elementor-repeater-item-0ee1239 jet-table__body-cell', 'energy_efficiency_class', 'Energieausweis'),
            ('jet-table__cell elementor-repeater-item-c022fe0 jet-table__body-cell', 'heating_type', 'Energieausweis')
        ]
        for search_class, prop, block_name in class_prop_pair:
            html_apt_prop = html_blocks[block_name].get_elements_by_class(search_class)
            if len(html_apt_prop) != 1:
                self.log_error_html_content_not_found('class', search_class)
            apt_raw[prop] = html_apt_prop[0].children[0].children[0].children[0].inner_html

        return apt_raw

    def map_apt_keys(self, apts_raw: list[dict]) -> list[dict]:
        apts_dicts = []
        for apt_raw in apts_raw:
            # extract zip code and place
            if apt_raw['zip_and_place'] is None:
                apt_raw['zip'] = None
                apt_raw['place'] = None
            else:
                try:
                    apt_raw['zip'] = int(apt_raw['zip_and_place'][:5])
                    apt_raw['place'] = apt_raw['zip_and_place'][6:]
                except (IndexError, ValueError):
                    apt_raw['zip'] = None
                    apt_raw['place'] = None
                    value = apt_raw['zip_and_place']
                    print(f'Warning: Cannot obtain zip code and place from "{value}"')

            # extract street and house number
            if apt_raw['street_and_number'] is None:
                apt_raw['street'] = None
                apt_raw['number'] = None
            else:
                try:
                    street_number_split = apt_raw['street_and_number'].split(' ')
                    if len(street_number_split) < 2:
                        raise ValueError
                    apt_raw['street'] = ' '.join(street_number_split[:-1])
                    apt_raw['house_number'] = int(street_number_split[-1])
                except ValueError:
                    apt_raw['street'] = None
                    apt_raw['house_number'] = None
                    value = apt_raw['street_and_number']
                    print(f'Warning: Cannot obtain street name and house number from "{value}"')

            # add exchange_apartment
            apt_raw['exchange_apartment'] = False
            apts_dicts.append(apt_raw)

        return apts_dicts
