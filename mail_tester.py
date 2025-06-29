from datetime import datetime

from config_loader import load_configuration
from utils import send_mail

if __name__ == '__main__':
    config = load_configuration()

    now = datetime.now()
    subject = f'Wohnungssucher Test Mail {now}'
    msg = 'This is a test mail initiated by the script "mail_tester".'
    send_mail(config['email_from_address'], config['email_to_address'], subject, msg_plain=msg)