import argparse
import configparser
import sys


class InvalidConfigOption(Exception):
    pass


class Config(object):
    def __init__(self, config_file='myndconfig.ini'):
        self._options = {}

        self.parse_config_file(config_file)
        # Command line arguments override config file args.
        self.parse_cmdline_args(sys.argv[1:])

    def get_option(self, section, option, default=None):
        try:
            value = self._options[section][option]
        except KeyError:
            value = default
        return value

    def parse_config_file(self, config_file):
        conf = configparser.ConfigParser()
        conf.read(config_file)

        self._options['irc'] = {}
        self._options['logging'] = {}

        self._options['irc']['server'] = conf.get('irc', 'server',
                                                  fallback=None)
        self._options['irc']['channel'] = conf.get('irc', 'channel',
                                                   fallback=None)
        self._options['irc']['nick'] = conf.get('irc', 'nickname',
                                                fallback='myndbot')
        self._options['irc']['port'] = conf.getint('irc', 'port',
                                                   fallback=6667)

        log_name = conf.get('logging', 'logger', fallback="Null")
        log_handler_name = "{}Handler".format(log_name.capitalize())
        self._options['logging']['logger'] = log_handler_name

        try:
            log_opts = dict(conf.items(log_name))
        except configparser.NoSectionError:
            log_opts = {}

        self._options['logging']['logger_opts'] = log_opts

    def parse_cmdline_args(self, argv):
        desc = "Myndbot IRC Bot"
        parser = argparse.ArgumentParser(description=desc)
        parser.add_argument('--irc-server',
                            required=False,
                            nargs='?',
                            help='IRC Server Address to connect to.'
                            )
        parser.add_argument('--irc-channel',
                            required=False,
                            nargs='?',
                            help='IRC Channel to connect to.'
                            )
        parser.add_argument('--irc-nick',
                            required=False,
                            nargs='?',
                            help='Nickname to use on the IRC server.'
                            )
        parser.add_argument('--irc-port',
                            required=False,
                            nargs='?',
                            type=int,
                            help='IRC Server Port to connect to.'
                            )

        args = parser.parse_args(argv)

        if args.irc_server:
            self._options['irc']['server'] = args.irc_server
        if args.irc_channel:
            self._options['irc']['channel'] = args.irc_channel
        if args.irc_nick:
            self._options['irc']['nick'] = args.irc_nick
        if args.irc_port:
            self._options['irc']['port'] = args.irc_port


# vim: ts=8 sts=4 sw=4 et
