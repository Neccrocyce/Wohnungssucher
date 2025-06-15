from email.policy import default

import user_configuration
from wohnungssucher_platforms.ws_mietwohnungsboerse import WSMietwohnungsboerse


def load_configuration():
    config = {
        'zips_included': user_configuration.zips_included,
        'zips_excluded': user_configuration.zips_excluded,
        'places_included': user_configuration.places_included,
        'places_excluded': user_configuration.places_excluded,
        'rent_cold_min': user_configuration.rent_cold_min,
        'rent_cold_max': user_configuration.rent_cold_max,
        'rent_warm_min': user_configuration.rent_warm_min,
        'rent_warm_max': user_configuration.rent_warm_max,
        'rooms_min': user_configuration.rooms_min,
        'rooms_max': user_configuration.rooms_max,
        'apartment_size_min': user_configuration.apartment_size_min,
        'apartment_size_max': user_configuration.apartment_size_max,
        'floors': user_configuration.floors,
        'energy_efficiency_classes': user_configuration.energy_efficiency_classes,
        'year_of_construction_min': user_configuration.year_of_construction_min,
        'year_of_construction_max': user_configuration.year_of_construction_max,
        'exchange_apartment': user_configuration.exchange_apartment,
        'path_files': user_configuration.path_files,
        'max_apartment_age': user_configuration.max_apartment_age
    }

    defaults = {
        'mietwohnungsboerse': user_configuration.defaults_mietwohnungsboerse
    }

    return config, defaults


if __name__ == '__main__':
    platforms = [
        'mietwohnungsboerse'
    ]
    config, defaults = load_configuration()

    # mietwohnungsboerse
    platform = WSMietwohnungsboerse(config, defaults[platforms[0]])
    platform()

