class OutlierException(Exception):
    def __init__(self, message, value):
        self.message = message
        self.value = value
