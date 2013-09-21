import pymongo


class BotLogger(object):
    def __init__(self, handlers=[], enabled=True):
        self.enabled = enabled
        self.handlers = handlers

    def enable_logging(self):
        self.enabled = True

    def disable_logging(self):
        self.enabled = False

    def add_handler(self, handler):
        if not isinstance(handler, Handler):
            raise ValueError("Attempt to add non-handler!")

        self.handlers.append(handler)

    def remove_handler(self, handler):
        if handler not in self.handlers:
            return

        handler.close()
        self.handlers.remove(handler)

    def log(self, msg, date, source, msg_type):
        if not self.enabled:
            return

        for handler in self.handlers:
            handler.log(msg, date, source, msg_type)


class Handler(object):
    def log(self, msg, date, source, msg_type):
        raise NotImplementedError("Abstract Method")

    def close(self):
        pass


class MongoHandler(Handler):
    def __init__(self, server='localhost',
                 database='irc',
                 collection='log',
                 port=27017):

        self.client = pymongo.MongoClient(server, int(port))
        self.db = self.client[database]
        self.collection = collection

    def log(self, msg, date, source, msg_type):
        self.db[self.collection].insert({
            "date": date,
            "type": msg_type,
            "content": msg,
            "source": source
        })

    def close(self):
        self.client.close()


class StdoutHandler(Handler):
    def log(self, msg, date, source, msg_type):
        print("{}|{}|{}|{}".format(date, msg_type, source, msg))


class NullHandler(Handler):
    def log(self, msg, date, source, msg_type):
        pass

# vim: ts=8 sts=4 sw=4 et
