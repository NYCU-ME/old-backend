class Logger:
    def __init__(self, prefix, logger):
        self.p      = f"[[{prefix}]]"
        self.logger = logger
    def info(self, msg):
        self.logger.info(self.p + " " + msg)
    def warning(self, msg):
        self.logger.info(self.p + " " + msg)
    def error(self, msg):
        self.logger.info(self.p + " " + msg)
