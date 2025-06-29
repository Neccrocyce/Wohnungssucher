import user_configuration


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
        'max_apartment_age': user_configuration.max_apartment_age,
        'email_from_address': user_configuration.email_from_address,
        'email_to_address': user_configuration.email_to_address,
        'email_send_status': user_configuration.email_send_status,
        'defaults_user': user_configuration.defaults,
        'notify_on_new_apartments_only': user_configuration.notify_on_new_apartments_only
    }

    return config