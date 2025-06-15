from core.utils import BoolPlus

#####################
# Apartment filters #
#####################
config = {
    'zips_included':  [12345],
    'zips_excluded': [],
    'places_included': None,
    'places_excluded': [],
    'rent_cold_min': 500,
    'rent_cold_max': 1300,
    'rent_warm_min': 0,
    'rent_warm_max': 1500,
    'rooms_min': 2,
    'rooms_max': None,
    'apartment_size_min': 50,
    'apartment_size_max': None,
    'floors': None,
    'energy_efficiency_classes': None,
    'year_of_construction_min': None,
    'year_of_construction_max': None,
    'exchange_apartment': BoolPlus.false(),
    'path_files': 'data',
    'max_apartment_age': None
}


####################
# Default settings #
####################

defaults_test = {
    'zip': True,
    'place': True,
    'rent_cold': True,
    'rent_warm': True,
    'room': True,
    'apartment_size': True,
    'floor': True,
    'energy_efficiency_class': True,
    'year_of_construction': True,
    'exchange_apartment': True
}


###################
# Common settings #
###################