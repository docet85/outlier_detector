class OutlierException(Exception):
    """
    Raised when a filter, configured with 'exception' strategy, hits an outlier.
    """

    def __init__(self, message: str, value: float):
        self.message = message
        """Context message"""
        self.value = value
        """The outlier value identified"""
