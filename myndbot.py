#!/usr/bin/env python3

import configparser
import datetime
import irc.bot
import irc.strings
import irclog


class MyndBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, logger, port=6667,
                 ns_pass=None):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname,
                                            nickname)
        self.channel = channel
        self.nickname = nickname
        self.ns_pass = ns_pass
        self.logger = logger

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        if self.ns_pass:
            self.authenticate()

        c.join(self.channel)

    def on_ctcp(self, c, e):
        msg = e.arguments[1]
        date = datetime.datetime.utcnow()
        source = e.source.nick
        self.logger.log(msg, date, source, "ctcp")

    def on_pubmsg(self, c, e):
        msg = e.arguments[0]
        date = datetime.datetime.utcnow()
        source = e.source.nick
        self.logger.log(msg, date, source, "msg")

        cmd_sentinel = '!'
        if msg.startswith(cmd_sentinel):
            self.do_command(e, msg[len(cmd_sentinel):].strip().split(' '))

    def authenticate(self):
        self.connection.notice("nickserv", "identify {}".format(ns_pass))

    def is_admin(self, nick):
        chan_obj = self.channels[self.channel]
        if nick in chan_obj.opers() or \
           nick in chan_obj.halfops() or \
           nick in chan_obj.owners():
            return True

        return False

    def do_command(self, e, cmd):
        nick = e.source.nick
        c = self.connection

        if cmd[0] == "die":
            if not self.is_admin(nick):
                c.notice(nick, "You cannot tell me to die!")
            else:
                self.die(msg="BAI BAI")

        elif cmd[0] == "kick":
            if not self.is_admin(nick):
                c.notice(nick, "I will not kick for you.")
            else:
                c.kick(self.channel, cmd[1])

        else:
            c.notice(nick, "Not understood: " + ' '.join(cmd))


def setup_logger(config):
    log_name = config.get('logging', 'logger', fallback="Null")
    log_handler_name = "{}Handler".format(log_name.capitalize())
    try:
        log_handler_type = getattr(irclog, log_handler_name)
    except AttributeError:
        raise RuntimeError("No handler for type {}, aborting!".format(
                           log_handler_name))
    try:
        log_opts = dict(config.items(log_name))
    except configparser.NoSectionError:
        log_opts = {}
    log_handler = log_handler_type(**log_opts)
    logger = irclog.BotLogger()
    logger.add_handler(log_handler)
    return logger


def main():
    config = configparser.ConfigParser()
    config.read('myndconfig.ini')
    logger = setup_logger(config)

    if not config.has_option('irc', 'server'):
        raise RuntimeError("No server provided! Aborting...")
    if not config.has_option('irc', 'channel'):
        raise RuntimeError("No channel provided! Aborting...")

    srv = config.get('irc', 'server')
    chan = config.get('irc', 'channel')
    nick = config.get('irc', 'nickname', fallback='myndbot')
    port = config.getint('irc', 'port', fallback=6667)

    bot = MyndBot(chan, nick, srv, logger, port=port)
    bot.start()

if __name__ == "__main__":
    main()

# vim: ts=8 sts=4 sw=4 et
