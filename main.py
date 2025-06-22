import copy
import json
import sys
import traceback
from datetime import datetime, time

import user_configuration
from apartment import Apartment
from utils import send_mail, send_error_mail, load_configuration
from wohnungssucher_platforms.ws_mietwohnungsboerse import WSMietwohnungsboerse


def filter_new_apts(apts: list[Apartment]) -> list[Apartment]:
    current_day = datetime.now().date()
    timestamp_today = datetime.combine(current_day, time(0, 0)).timestamp()
    timestamp_max_age = timestamp_today - 604800  # one week 7*24*60*60s

    apts_new = []
    for apt in apts:
        if apt.released > timestamp_max_age:
            apts_new.append(apt)
    return apts_new

def filter_new_errors(errors: list[dict]) -> list[dict]:
    current_day = datetime.now().date()
    timestamp_today = datetime.combine(current_day, time(0, 0)).timestamp()
    timestamp_max_age = timestamp_today - 604800  # one week 7*24*60*60s

    errors_new = []
    for err in errors:
        if err['timestamp'] > timestamp_max_age:
            errors_new.append(err)
    return errors_new


if __name__ == '__main__':
    platforms = [
        ('mietwohnungsboerse', WSMietwohnungsboerse)
    ]
    config, defaults = load_configuration()

    # send weekly status report if monday
    if config['email_send_status'] and datetime.now().weekday() == 0:
        config_dict = copy.deepcopy(config)
        config_dict['exchange_apartment'] = str(config['exchange_apartment'])

        report = {
            'Status': 'running',
            'User Settings': config_dict,
            'User Settings Defaults': defaults,
            'Apartment Portals': [x[0] for x in platforms]
        }

        num_apts_new_tot_0 = 0
        num_apts_new_tot_1 = 0
        num_critical_errors = 0
        num_noncritical_errors = 0

        for desc, func in platforms:
            platform = func(config, defaults[desc])
            apts_0 = filter_new_apts(platform.load_apartments(platform.path_savefile_0))
            apts_1 = filter_new_apts(platform.load_apartments(platform.path_savefile_1))
            errors = filter_new_errors(platform.load_errors())
            errors_critical = [x for x in errors if x['type'] == 'CRITICAL']
            errors_noncritical = [x for x in errors if x['type'] == 'ERROR']

            num_apts_new_tot_0 += len(apts_0)
            num_apts_new_tot_1 += len(apts_1)
            num_critical_errors += len(errors_critical)
            num_noncritical_errors += len(errors_noncritical)

            report_apt = {
                'New apartments': {
                    'Counts': {
                        'Total': len(apts_0) + len(apts_1),
                        'Category 0': len(apts_0),
                        'Category 1': len(apts_1),
                    },
                    'Details': {
                        'Category 0': [x.to_dict() for x in apts_0],
                        'Category 1': [x.to_dict() for x in apts_1]
                    }
                },
                'Errors': {
                    'Counts': {
                        'Total': len(errors),
                        'Critical': len(errors_critical),
                        'Non-Critical': len(errors_noncritical),
                    },
                    'Details': {
                        'Critical': errors_critical,
                        'Non-Critical': errors_noncritical,
                    }
                }
            }
            report[desc] = report_apt

        msg = f'Total number of new apartments: {num_apts_new_tot_0}\n'
        msg += f'Total number of further apartments (with missing properties): {num_apts_new_tot_1}\n'
        msg += f'Total number of errors: {num_critical_errors} critical errors, {num_noncritical_errors} non-critical errors\n\n'
        msg += json.dumps(report, indent=2)

        subject = 'Status report Wohnungssucher'
        send_mail(config['email_from_address'], config['email_to_address'], subject, msg_plain=msg)


    # look for new apartments
    for desc, cls in platforms:
        platform = cls(config, defaults[desc])
        try:
            platform()
        except:
            msg = traceback.format_exc()
            send_error_mail(config['email_from_address'], config['email_to_address'], msg)
            platform.log_error(msg, critical=True)
            platform.save_errors()




