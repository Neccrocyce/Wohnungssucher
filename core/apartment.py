from __future__ import annotations

from datetime import datetime, time
from typing import Any

from core.utils import BoolPlus


class Apartment:
    # Unique ID of the apartment
    id: Any

    # Short description of the apartment
    description: str | None

    # url referencing to the apartment on the corresponding webpage
    url: str

    # address of the apartment: zip code, place, street and house number
    zip: int | None
    place: str | None
    street: str | None
    house_number: int | None

    # rent without heating (Kaltmiete)
    rent_cold: int | None

    # rent with heating (Warmmiete)
    rent_warm: int | None

    # number of rooms (Anzahl Zimmer)
    rooms: float | None

    # living space of the apartment (Wohnflaeche)
    apartment_size: float | None

    # Floor the apartment is situated (Etage)
    floor: int | None

    # Year of construction (Baujahr)
    year_of_construction: int | None

    # Type of heating, e.g., Gas, oil, ... (Heizungsart)
    heating_type: str | None

    # energy efficiency class of the apartment (Energieeffizienzklasse)
    energy_efficiency_class: str | None

    # Whether it is an exchange apartment (Tauschwohnung)
    exchange_apartment: bool | None

    # Timestamp of the day the apartment was first listed on the webpage
    released: int

    def __init__(
            self,
            id: Any,
            description: str | None,
            url: str,
            zip: int | None,
            place: str | None,
            street: str | None,
            house_number: int | None,
            rent_cold: int | None,
            rent_warm: int | None,
            rooms: float | None,
            apartment_size: float | None,
            floor: int | None,
            year_of_construction: int | None,
            heating_type: str | None,
            energy_efficiency_class: str | None,
            exchange_apartment: bool | None,
            released: int
    ):
        self.id = id
        self.description = description
        self.url = url
        self.zip = zip
        self.place = place
        self.street = street
        self.house_number = house_number
        self.rent_cold = rent_cold
        self.rent_warm = rent_warm
        self.rooms = rooms
        self.apartment_size = apartment_size
        self.floor = floor
        self.year_of_construction = year_of_construction
        self.heating_type = heating_type
        self.energy_efficiency_class = energy_efficiency_class
        self.exchange_apartment = exchange_apartment
        self.released = released

    @classmethod
    def from_dict(cls, attr: dict) -> Apartment:
        """
        Create an object from a dictionary which contains the values for all class attributes.
        The values for all attributes must be stored in attr even if the value is None.
        Only the value for the attribute "released" is optional.
        If the dictionary does not contain the key "released", the timestamp of the current day will set for this
        attribute.
        :param attr: dictionary containing the values for all class attributes
        :return:
        """
        if 'released' not in attr.keys():
            current_day = datetime.now().date()
            attr['released'] = datetime.combine(current_day, time(0, 0))

        return Apartment(
            id=attr['id'],
            description=attr['description'],
            url=attr['url'],
            zip=attr['zip'],
            place=attr['place'],
            street=attr['street'],
            house_number=attr['house_number'],
            rent_cold=attr['rent_cold'],
            rent_warm=attr['rent_warm'],
            rooms=attr['rooms'],
            apartment_size=attr['apartment_size'],
            floor=attr['floor'],
            year_of_construction=attr['year_of_construction'],
            heating_type=attr['heating_type'],
            energy_efficiency_class=attr['energy_efficiency_class'],
            exchange_apartment=attr['exchange_apartment'],
            released=attr['released']
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'description': self.description,
            'url': self.url,
            'zip': self.zip,
            'place': self.place,
            'street': self.street,
            'house_number': self.house_number,
            'rent_cold': self.rent_cold,
            'rent_warm': self.rent_warm,
            'rooms': self.rooms,
            'apartment_size': self.apartment_size,
            'floor': self.floor,
            'year_of_construction': self.year_of_construction,
            'heating_type': self.heating_type,
            'energy_efficiency_class': self.energy_efficiency_class,
            'exchange_apartment': self.exchange_apartment,
            'released': self.released
        }

    def get_address(self):
        return f'{self.street} {self.house_number}\n{self.zip} {self.place}'

    @staticmethod
    def _check_inexcluded(
            value: Any | None,
            values_included: list[Any] | None,
            values_excluded: list[Any],
            default: bool
    ) -> bool:
        """
        Checks if value  is included in values_included and is not included in values_excluded.
        If values_included is None, it is treated as all available values and therefore True is returned.
        :param values_included: list of all values in which value should be.
        :param values_excluded: list of all values in which value should not be.
        :param default: If value is none, default is returned or True if values_included is None
        :return:
        """
        if value is None:
            if values_included is None:
                return True
            else:
                return default

        if value in values_excluded:
            return False

        if values_included is not None:
            if value in values_included:
                return True
            else:
                return False
        else:
            return True


    @staticmethod
    def _check_within(
            value: int | float | None,
            value_min: int | float,
            value_max: int | float,
            default: bool
    ) -> bool:
        """
        Checks if value is greater or equal than value_min and less or equal to value_max.
        :param value_min:
        :param value_max:
        :param default: If value is none, default is returned
        :return:
        """
        if value is None:
            return default

        if value_min <= value <= value_max:
            return True
        else:
            return False

    @staticmethod
    def _check_in_list(value: Any | None, allowed_values: list[Any] | None, default: bool) -> bool:
        """
        Checks if value is included in allowed_values
        If allowed_values is None, it is treated as all available values and therefore True is returned.
        :param allowed_values: list of values to check against.
        :param default: If value is none, default is returned or True if allowed_values is None
        :return:
        """
        if value is None:
            if allowed_values is None:
                return True
            else:
                return default

        if allowed_values is None:
            return True
        else:
            return value in allowed_values

    def check_zip(self, zips_included: list[int] | None, zips_excluded:  list[int], default = False) -> bool:
        """
        Checks if the zip code of the apartments is included in zips_included and is not included in zips_excluded.
        If zips_included is None, it is treated as all available zip codes and therefore this apartment is included.
        :param zips_included: list of all zip codes in which this apartment should be placed.
        :param zips_excluded: list of all zip codes in which this apartment should not be placed.
        :param default: If self.zip is none, default is returned
        :return:
        """
        return self._check_inexcluded(self.zip, zips_included, zips_excluded, default)

    def check_place(self, places_included: list[str] | None, places_excluded:  list[str], default = False) -> bool:
        """
        Checks if the place of the apartments is included in places_included and is not included in places_excluded.
        If places_included is None, it is treated as all available zip codes and therefore this apartment is included.
        :param places_included: list of all places in which this apartment should be.
        :param places_excluded: list of all places in which this apartment should not be.
        :param default: If self.zip is none, default is returned
        :return:
        """
        return self._check_inexcluded(self.place, places_included, places_excluded, default)

    def check_rent_cold(self, rent_min: int, rent_max: int, default = False) -> bool:
        return self._check_within(self.rent_cold, rent_min, rent_max, default)

    def check_rent_warm(self, rent_min: int, rent_max: int, default = False) -> bool:
        return self._check_within(self.rent_warm, rent_min, rent_max, default)

    def check_rooms(self, rooms_min: int, rooms_max: int, default = False) -> bool:
        return self._check_within(self.rooms, rooms_min, rooms_max, default)

    def check_apartment_size(self, apartment_size_min: int, apartment_size_max: int, default = False) -> bool:
        return self._check_within(self.apartment_size, apartment_size_min, apartment_size_max, default)

    def check_floor(self, allowed_floors: list[int] | None, default = False) -> bool:
        """
        Checks if the apartment floor is included in allowed_floors
        If allowed_floors is None, it is treated as all available floors and therefore this apartment is included.
        :param allowed_floors: list of all available floors on which this apartment can be.
        :param default: If self.zip is none, default is returned
        :return:
        """
        return self._check_in_list(self.floor, allowed_floors, default)

    def check_energy_efficiency_class(
            self,
            allowed_energy_efficiency_classes: list[str] | None,
            default = False
    ) -> bool:
        """
        Checks if the apartment floor is included in allowed_floors
        If allowed_energy_efficiency_classes is None, it is treated as all available floors and therefore this apartment is included.
        :param allowed_energy_efficiency_classes: list of all allowed energy efficiency classes for this apartment.
        :param default: If self.zip is none, default is returned
        :return:
        """
        return self._check_in_list(self.energy_efficiency_class, allowed_energy_efficiency_classes, default)

    def check_year_of_construction(
            self,
            year_of_construction_min: int,
            year_of_construction_max: int,
            default = False
    ) -> bool:
        return self._check_within(self.year_of_construction, year_of_construction_min, year_of_construction_max, default)

    def check_exchange_apartment(self, allowed_exchange_apartment: BoolPlus, default = False) -> bool:
        if self.exchange_apartment is None:
            return default
        else:
            return self.exchange_apartment == allowed_exchange_apartment