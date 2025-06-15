
"""
Configure all settings here
"""
from core.utils import BoolPlus

"""
#####################
# Apartment filters #
#####################
Set any value to None to ignore it
"""

# All zip codes an apartments can be located (Postleitzahlen inklusive).
# e.g., [80331, 85560]
zips_included: list[int] | None = None

# All zip codes an apartments should not be located (Postleitzahlen exklusive).
# e.g., [10178, 10365]
zips_excluded: list[int] | None= []

# All places an apartments can be located (Orte inklusive).
# e.g., ['München', 'Augsburg']
places_included: list[str] | None = None

# All places an apartments should not be located (Orte exklusive.
# e.g., ['Berlin']
places_excluded: list[str] | None = []

# Lowest acceptable rental price for an apartment excluding heating (Minimum Kaltmiete)
# e.g., 500
rent_cold_min: int | None = 500

# Highest acceptable rental price for an apartment excluding heating (Maximum Kaltmiete)
# e.g., 3000
rent_cold_max: int | None = 2000

# Lowest acceptable rental price for an apartment including heating (Minimum Warmmiete)
# e.g., 500
rent_warm_min: int | None = None

# Highest acceptable rental price for an apartment including heating (Maximum Warmmiete)
# e.g., 3000
rent_warm_max: int | None = None

# Minimum number of rooms an apartment must have (Minimum Anzahl Zimmer)
# e.g., 2
rooms_min: int | None = 2

# Maximum number of rooms an apartment must have (Maximum Anzahl Zimmer)
# e.g., 5
rooms_max: int | None = None

# The smallest acceptable living space for an apartment, measured in square meters (Minimum Wohnflaeche in m^2)
# e.g., 50
apartment_size_min: int | None = 40

# The largest acceptable living space for an apartment, measured in square meters (Maximum Wohnflaeche in m^2)
# e.g., 100
apartment_size_max: int | None = None

# Range of floors where an apartment can be situated within a building. (Ground floor = 0) (Etagen)
# e.g., [0, 1, 2]
floors: list[int] | None = None

# Acceptable energy efficiency classes for an apartment (Energieeffizienzklassen)
# Valid Values: A+, A, B, C, D, E, F, G, H
# e.g., ['A+', 'B']
energy_efficiency_classes: list[str] | None = None

# Earliest acceptable construction year for an apartment (Minimum Baujahr)
# e.g., 1900
year_of_construction_min: int | None = None

# Latest acceptable construction year for an apartment (Maximum Baujahr)
# e.g., 2025
year_of_construction_max: int | None = None

# Whether an apartment can be an exchange apartment, which refers to a housing arrangement where two parties agree to
# swap their apartments for a certain period (Tauschwohnung)
# Valid values:
# - BoolPlus.false(): Apartment must not be an exchange apartment
# - BoolPlus.true(): Apartment must be an exchange apartment
# - BoolPlus.maybe() or None: Apartment can be an exchange apartment
exchange_apartment: BoolPlus | None = BoolPlus.false()

"""
#####################
# Default settings #
#####################
These settings define whether an apartment should be listed if it has no information about a specific property.
Set the corresponding value to true to accept apartments.
These apartments will be listed separately to those ones providing all information.

Zip code (Postleitzahl)
Place (Ort)
Rental price without heating (Kaltmiete)
Rental price with heating (Warmmiete)
Number of rooms (Anzahl Zimmer)
Living space of an apartment (Wohnfläche)
floor in which the apartment is situated (Etage)
Energy efficiency class (Energieeffizienzklasse)
year of construction (Baujahr)
Exchange Apartment (Tauschwohnung)
"""

defaults_mietwohnungsboerse = {
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


"""
#####################
# Common settings #
#####################

"""
# path to all savefiles
path_files: str = 'data'

# Remove all apartments from the savefile which are older than this number of days.
# Make sure to select a number that is higher than the number of days the apartment is listed on the webpage
# After removal if the apartment is still on the webpage it will be considered as new apartment on the next run.
# Set to None to ignore
max_apartment_age: int | None = None