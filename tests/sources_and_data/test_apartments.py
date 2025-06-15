"""
List of dummy apartments for testing
"""
from apartment import Apartment

apt_00 = {
    'id': 0,
    'description': 'Apartment 00',
    'url': 'dummy_url_00',
    'zip': 12345,
    'place': 'Eins Zwei Drei Vier Fünf',
    'street': 'Teststraße',
    'house_number': 0,
    'rent_cold': 980,
    'rent_warm': 1200,
    'rooms': 2.0,
    'apartment_size': 55.0,
    'floor': 1,
    'year_of_construction': 2000,
    'heating_type': 'Fernwärme',
    'energy_efficiency_class': 'C',
    'exchange_apartment': False
}

apt_01 = {
    'id': 1,
    'description': 'Apartment 01',
    'url': 'dummy_url_01',
    'zip': 12345,
    'place': 'Eins Zwei Drei Vier Fünf',
    'street': 'Teststraße',
    'house_number': 1,
    'rent_cold': 780,
    'rent_warm': 910,
    'rooms': 2.0,
    'apartment_size': 50.0,
    'floor': 5,
    'year_of_construction': 1930,
    'heating_type': 'Öl',
    'energy_efficiency_class': 'E',
    'exchange_apartment': False
}

apt_02 = {
    'id': 2,
    'description': 'Apartment 02',
    'url': 'dummy_url_02',
    'zip': 12345,
    'place': 'Eins Zwei Drei Vier Fünf',
    'street': 'Prüfstraße',
    'house_number': 2,
    'rent_cold': None, #1300,
    'rent_warm': 1500,
    'rooms': 2.5,
    'apartment_size': 60.0,
    'floor': 0,
    'year_of_construction': 1999,
    'heating_type': 'Fernwärme',
    'energy_efficiency_class': 'C',
    'exchange_apartment': False
}

apt_03 = {
    'id': 3,
    'description': 'Apartment 03',
    'url': 'dummy_url_03',
    'zip': 12345,
    'place': 'Eins Zwei Drei Vier Fünf',
    'street': 'Unitgasse',
    'house_number': 3,
    'rent_cold': 1630,
    'rent_warm': 1980,
    'rooms': 3.0,
    'apartment_size': 63.0,
    'floor': 3,
    'year_of_construction': 1973,
    'heating_type': 'Gas',
    'energy_efficiency_class': 'D',
    'exchange_apartment': False
}

apt_04 = {
    'id': 4,
    'description': 'Apartment 04',
    'url': 'dummy_url_04',
    'zip': 34567,
    'place': 'Drei Vier Fünf Sechs Sieben',
    'street': 'Checkallee',
    'house_number': 4,
    'rent_cold': 980,
    'rent_warm': 1170,
    'rooms': 2.0,
    'apartment_size': 56.0,
    'floor': 2,
    'year_of_construction': 2003,
    'heating_type': 'Wärmepumpe',
    'energy_efficiency_class': 'A',
    'exchange_apartment': False
}

apartments = [apt_00, apt_01, apt_02, apt_03, apt_04]