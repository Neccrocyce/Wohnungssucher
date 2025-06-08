import re

from core.apartment import Apartment
from core.wohnungssucher_base import WohnungssucherBase
import requests

##############################
# AVAILABILITY OF ATTRIBUTES #
##############################
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

url = 'https://www.mietwohnungsboerse.de/Immobilien.htm?action_form=search&vermarktungsart=MIETE_PACHT&plz=8%2C9'

class WSMietwohnungsboerse(WohnungssucherBase):
    def __init__(self, config, defaults):
        config['url_platform'] = url
        super().__init__(config, defaults)

    def request_all_apartments(self) -> list[Apartment]:
        html_full = self.request_url(self.url_platform)
        html_apartments = html_full.get_element_by_id('immo-container-results')
        if html_apartments is None:
            raise ValueError('Cannot find id "immo-container-results" in response. Maybe webpage has been modified?')

        for html_apartments_each in html_apartments.children:
            url_part = html_apartments_each.children[1].children[0].attributes['href']
            url = self.parse_url(self.url_platform, url_part)
            html_apartment = self.request_url(url)

        pass

    def extract_apartments(self, html: str) -> list[Apartment]:
        """
        Takes an html content containing all apartments and extracts each apartment from it.
        :param html:
        :return: list of all apartments
        """
        pass