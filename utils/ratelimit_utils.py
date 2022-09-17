"""
Decorators that control API calls
"""
from functools import wraps
import logging
import time
import threading

from utils.exception import RateLimitException


class RateLimit(object):
    """ Decorator that Limits the number of times a function is called in a time interval. 

    Parameters
    ----------
    calls: int
        Maximum number of times a function can be executed in time period.
    interval: int
        Time period before the number of calls reset.
    raise_on_limit: bool, default=True
        Raises ratelimitexception when all number of calls have been used up in interval. 
        Recommended to be used with sleep_and_retry decorator to sleep until interval is up
        and calls are replenished.

    Attributes
    ----------
    calls: int
        Desired max mumber of calls per time period.
    interval: int
        Desired time period before number of calls replenish.
    raise_on_limit: bool
        If user wants to raise ratelimit exception.
    clock: function
        function being used to calculate current time.
    last_reset: float
        Last time interval was reset.
    num_calls: int
        Total calls made in an interval.
    lock: function
        Type of thread locker to use.
    
    Methods
    -------
    __call__
        Creates the decorator for a function.
    """
    def __init__(self, calls, interval, raise_on_limit=True):
        self.calls = calls
        self.interval = interval
        self.clock = time.monotonic
        self.raise_on_limit = raise_on_limit

        # Initialise the decorator state.
        self.last_reset = time.monotonic()
        self.num_calls = 0

        # Add thread safety.
        self.lock = threading.RLock()


    def __call__(self, func):
        """
        Creates a wrapped function that prevents function invocations if previously called 
        within a specific period of time.

        Parameters
        ----------
        func: function
            Desired function to decorate.

        Returns
        -------
        function
            The decorated input function.
        """
        @wraps(func)
        def wrapper(*args, **kargs):
            """
            Used to determine the behavior of the wrapped function. It forwards function invocations
            previously called no sooner than a specified period of time.

            Parameters
            ----------
            args: 
                non-keyword variable length argument list to the decorated function.
            kargs: 
                keyworded variable length argument list to the decorated function.

            Returns
            -------
            function
                Input function with all passed parameters. If rate limit exception is raised it
                returns None.
            """
            # creates a thread lock using context manager
            with self.lock:
                # finding the time between the previous call and now.
                elapsed = self.clock() - self.last_reset

                # determing how much time has passed in the interval
                period_remaining = self.interval - elapsed

                # if the time window has concluded then reset.
                if period_remaining <= 0:
                    self.num_calls = 0
                    self.last_reset = self.clock()

                # Increase the number of attempts to call the function.
                self.num_calls += 1

                # If the number of attempts to call the function exceeds the
                # maximum then raise an exception.
                if self.num_calls > self.calls:
                    if self.raise_on_limit:
                        raise RateLimitException(period_remaining)
                    return

            return func(*args, **kargs)
        return wrapper


def sleep_and_retry(func):
    """
    Return a wrapped function that rescues rate limit exceptions, sleeping the
    current thread until rate limit resets.

    Parameters
    ----------
    func: function
        Desired function to decorate

    Returns
    -------
    function
        Decorated function.
    """
    @wraps(func)
    def wrapper(*args, **kargs):
        """
        Used to determine the behavior of the wrapped function. Calls the rate limited function. 
        If the function raises a rate limit exception sleep for the remaining period and retry 
        the function.

        Parameters
        ----------
        args: 
            non-keyword variable length argument list to the decorated function.
        kargs: 
            keyworded variable length argument list to the decorated function.

        Returns
        -------
        function
            Input function with all passed parameters. 
        """
        # looping until function does not return ratelimit exception. Sleeping otherwise.
        while True:
            try:
                return func(*args, **kargs)
            except RateLimitException as exception:
                logging.warning(f'{exception} Sleeping for {round(exception.time_remaining, 2)} seconds.')
                time.sleep(exception.time_remaining)
    return wrapper