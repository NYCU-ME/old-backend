
def checkLevel(level):
    def decorator(func):
        def wrap(self, msg):
            if level <= self.level:
                return func(msg, level)
        return wrap
    return decorator

class Logger:

    def __init__(self, prefix, logger, level):
        self.p      = f"[[{prefix}]]"
        self.logger = logger
        self.level  = level

    @checkLevel(4)
    def debug(self, msg):
        self.logger.info(self.p + " " + msg)

    @checkLevel(3)
    def info(self, msg):
        self.logger.info(self.p + " " + msg)

    @checkLevel(2)
    def warning(self, msg):
        self.logger.info(self.p + " " + msg)

    @checkLevel(1)
    def error(self, msg):
        self.logger.info(self.p + " " + msg)

