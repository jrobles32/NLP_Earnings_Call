"""
Rate limit exception
"""
class RateLimitException(Exception):
    """
    Custom exception raise when the number of function invocations exceedsthat imposed by a rate 
    limit. Additionally the exception is aware of the remaining time period after which the rate 
    limit is reset.

    Parameters
    ----------
    message: str
        Custom exception message.
    period_remaining: float
        The time remaining until the rate limit is reset.
    """
    def __init__(self, time_remaining,  message='API calls have reached rate limit.'):
        super().__init__(message)
        self.time_remaining = time_remaining
    