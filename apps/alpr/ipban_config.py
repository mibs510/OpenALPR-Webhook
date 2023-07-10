import configparser
from os.path import exists


class IPBanConfig:
    ban_count = 20
    ban_seconds = 86400
    persist = False
    ip_header = ""
    abuse_IPDB_config_report = False
    abuse_IPDB_config_load = False
    abuse_IPDB_config_key = ""
    record_dir = "logs/ipban"

    config = configparser.ConfigParser()

    def __init__(self):
        # Set up ipban ini file with defaults if it doesn't exist
        if not exists("ipban.ini"):
            self.save()

        self.read()

    def get_settings(self) -> {}:
        persist = True if self.persist == "True" else False
        abuse_IPDB_config_report = True if self.abuse_IPDB_config_report == "True" else False
        abuse_IPDB_config_load = True if self.abuse_IPDB_config_load == "True" else False

        return {
            'ban_count': self.ban_count, 'ban_seconds': self.ban_seconds, 'persist': persist,
            'ip_header': self.ip_header, 'abuse_IPDB_config_report': abuse_IPDB_config_report,
            'abuse_IPDB_config_load': abuse_IPDB_config_load,
            'abuse_IPDB_config_key': self.abuse_IPDB_config_key
        }

    def read(self) -> None:
        # Create a config obj
        self.config = configparser.ConfigParser()
        # Read from the ini file
        self.config.read("ipban.ini")

        # (Re)Populate this obj
        self.ban_count = self.config['ipban']['ban_count']
        self.ban_seconds = self.config['ipban']['ban_seconds']
        self.persist = self.config['ipban']['persist']
        self.ip_header = self.config['ipban']['ip_header']
        self.abuse_IPDB_config_report = self.config['ipban']['abuse_IPDB_config_report']
        self.abuse_IPDB_config_load = self.config['ipban']['abuse_IPDB_config_load']
        self.abuse_IPDB_config_key = self.config['ipban']['abuse_IPDB_config_key']

    def save(self) -> None:
        self.config['ipban'] = {'ban_count': self.ban_count, 'ban_seconds': self.ban_seconds, 'persist': self.persist,
                                'ip_header': self.ip_header,
                                'abuse_IPDB_config_report': self.abuse_IPDB_config_report,
                                'abuse_IPDB_config_load': self.abuse_IPDB_config_load,
                                'abuse_IPDB_config_key': self.abuse_IPDB_config_key,
                                'record_dir': self.record_dir
                                }
        with open("ipban.ini", 'w', encoding='utf-8') as ini:
            self.config.write(ini)
