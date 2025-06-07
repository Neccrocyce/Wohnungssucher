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

class WSMietwohnungsboerse(WohnungssucherBase):
    url = 'https://www.mietwohnungsboerse.de/Immobilien.htm?action_form=search&vermarktungsart=MIETE_PACHT&plz=8%2C9'

    def __init__(self, config, defaults):
        super().__init__()
        config['url_platform'] = self.url
        self.set_from_cfg(config, defaults)

    def load_all_apartments(self) -> str:
        response = requests.get(self.url_platform)
        # todo
        return response.content

    def extract_apartments(self, html: str) -> list[Apartment]:
        """
        Takes an html content containing all apartments and extracts each apartment from it.
        :param html:
        :return: list of all apartments
        """
        pass