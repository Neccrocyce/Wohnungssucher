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
        'exchange_apartment': user_configuration.exchange_apartment
    }

    defaults = {
        'zip': user_configuration.default_zip,
        'place': user_configuration.default_place,
        'rent_cold': user_configuration.default_rent_cold,
        'rent_warm': user_configuration.default_rent_warm,
        'room': user_configuration.default_room,
        'apartment_size': user_configuration.default_apartment_size,
        'floor': user_configuration.default_floor,
        'energy_efficiency_class': user_configuration.default_energy_efficiency_class,
        'year_of_construction': user_configuration.default_year_of_construction,
        'exchange_apartment': user_configuration.default_exchange_apartment,
    }

    return config, defaults


if __name__ == '__main__':
    config, defaults = load_configuration()
    platform = WSMietwohnungsboerse(config, defaults)
    page = platform.load_all_apartments()

    with open('data.html', 'w') as f:
        f.write(str(page))