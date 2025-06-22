from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Literal

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
        'defaults_user': user_configuration.defaults
    }

    return config


def send_mail(from_addr: str, to_addr: str, subject: str, msg_plain: str = '', msg_html: str = ''):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr

    if msg_plain:
        msg.attach(MIMEText(msg_plain, 'plain'))
    if msg_html:
        msg.attach(MIMEText(msg_html, 'html'))

    with smtplib.SMTP('localhost') as server:
        server.sendmail(from_addr=from_addr, to_addrs=to_addr, msg=msg.as_string())

def send_error_mail(from_addr, to_addr, msg):
    subject = 'Critical error occurred during the execution of Wohnungssucher'
    if user_configuration.email_send_status:
        send_mail(from_addr, to_addr, subject, msg_plain=msg)


class BoolPlus:
    """
    This class extends the classic boolean by a new value "Maybe".
    This means that objects can have the following states:
    - True
    - False
    - Maybe

    In addition to the classic rules, BoolPlus follows the following rules:
    These kinds of comparison can also be used with classic bool values (a: bool == b: BoolPlus)
    True == Maybe: True
    False == Maybe: True

    These kinds of operation must be executed using the functions implemented in this class.
    DO NOT USE THE STANDARD AND, OR, ...
    Maybe and True: True
    Maybe and False: False
    Maybe and Maybe: Maybe
    Maybe or False: True
    Maybe or True: True
    Maybe or Maybe: True
    Not Maybe: Maybe
    """
    value: int = -1

    def __init__(self, value: Literal[0, 1, 2]):
        if self.value == -1:
            raise TypeError("BoolPlus objects must be created using the 'init_false', 'init_true' and 'init_maybe'!")
        assert 0 <= value <= 2
        self.value = value

    @classmethod
    def false(cls):
        cls.value = 0
        return cls(0)

    @classmethod
    def true(cls):
        cls.value = 0
        return cls(1)

    @classmethod
    def maybe(cls):
        cls.value = 0
        return cls(2)

    @staticmethod
    def check_internal_state(bool_plus: BoolPlus):
        if not 0 <= bool_plus.value <= 2:
            raise ValueError(f"Invalid state of variable value with value {bool_plus.value}")

    def NOT(self):
        self.check_internal_state(self)
        if self.value == 0:
            return BoolPlus.true()
        elif self.value == 1:
            return BoolPlus.false()
        else:
            return self

    def AND(self, other: BoolPlus | bool):
        if isinstance(other, bool):
            if other:
                other = BoolPlus.true()
            else:
                other = BoolPlus.false()

        self.check_internal_state(self)
        self.check_internal_state(other)

        if self.value == 2:
            return other
        elif other.value == 2:
            return self
        else:
            if self.value and other.value:
                return BoolPlus.true()
            else:
                return BoolPlus.false()

    def OR(self, other: BoolPlus | bool):
        if isinstance(other, bool):
            if other:
                other = BoolPlus.true()
            else:
                other = BoolPlus.false()

        self.check_internal_state(self)
        self.check_internal_state(other)

        if self.value == 2 or other.value == 2:
            return True
        else:
            if self.value or other.value:
                return BoolPlus.true()
            else:
                return BoolPlus.false()

    def __eq__(self, other: BoolPlus | bool):
        if isinstance(other, bool):
            if other:
                other = BoolPlus.true()
            else:
                other = BoolPlus.false()

        self.check_internal_state(self)
        self.check_internal_state(other)

        if self.value == 2 or other.value == 2:
            return True
        else:
            return self.value == other.value

    def __str__(self):
        self.check_internal_state(self)

        if self.value == 0:
            return "False"
        elif self.value == 1:
            return "True"
        else:
            return "Maybe"

    def __repr__(self):
        return self.__str__()
