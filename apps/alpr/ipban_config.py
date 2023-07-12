#  Copyright (c) 2023. Connor McMillan
#  Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
#  following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#  disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#  following disclaimer in the documentation and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#  products derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES,
#  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

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
