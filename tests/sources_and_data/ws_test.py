import os.path

from sources_and_data import test_apartments
from apartment import Apartment
from wohnungssucher_base import WohnungssucherBase

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

class WSTest(WohnungssucherBase):

    def __init__(self, config, defaults_user):
        path_savefile_0 = str(os.path.join(config['path_files'], 'tests_0.json'))
        path_savefile_1 = str(os.path.join(config['path_files'], 'tests_1.json'))
        super().__init__(config, defaults_0, defaults_user,'dummy_url_ws_test', path_savefile_0, path_savefile_1)

    def request_all_apartments(self) -> list[Apartment]:
        apartments = []
        for apt in test_apartments.apartments:
            apartments.append(Apartment.from_dict(apt))

        return apartments