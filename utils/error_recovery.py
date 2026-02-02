"""
Error Recovery System
Robust error handling for production deployment
"""

import time
import logging
from typing import Callable, Any, Optional
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(self,
                 max_attempts: int = 3,
                 initial_delay: float = 1.0,
                 backoff_factor: float = 2.0,
                 max_delay: float = 60.0):
        """
        Initialize retry configuration
        
        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay between retries (seconds)
            backoff_factor: Exponential backoff multiplier
            max_delay: Maximum delay between retries (seconds)
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay


def retry_on_error(config: Optional[RetryConfig] = None,
                   exceptions: tuple = (Exception,),
                   on_retry: Optional[Callable] = None):
    """
    Decorator to retry function on error with exponential backoff
    
    Args:
        config: Retry configuration
        exceptions: Tuple of exceptions to catch
        on_retry: Optional callback function called on each retry
        
    Usage:
        @retry_on_error(config=RetryConfig(max_attempts=3))
        def my_function():
            pass
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = config.initial_delay
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    if attempt == config.max_attempts:
                        logger.error(f"{func.__name__} failed after {config.max_attempts} attempts: {e}")
                        raise
                    
                    logger.warning(f"{func.__name__} failed (attempt {attempt}/{config.max_attempts}): {e}")
                    logger.info(f"Retrying in {delay:.1f}s...")
                    
                    # Call retry callback if provided
                    if on_retry:
                        on_retry(attempt, e)
                    
                    time.sleep(delay)
                    
                    # Exponential backoff
                    delay = min(delay * config.backoff_factor, config.max_delay)
            
            return None
        
        return wrapper
    
    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern for fault tolerance
    
    States:
    - CLOSED: Normal operation
    - OPEN: Too many failures, reject requests
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 expected_exception: type = Exception):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call function through circuit breaker
        
        Args:
            func: Function to call
            *args, **kwargs: Function arguments
            
        Returns:
            Function result
            
        Raises:
            Exception if circuit is open
        """
        # Check if circuit is open
        if self.state == 'OPEN':
            # Check if recovery timeout passed
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                logger.info("Circuit breaker: Attempting recovery (HALF_OPEN)")
                self.state = 'HALF_OPEN'
            else:
                raise Exception(f"Circuit breaker is OPEN (too many failures)")
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset if in HALF_OPEN
            if self.state == 'HALF_OPEN':
                logger.info("Circuit breaker: Recovery successful (CLOSED)")
                self.state = 'CLOSED'
                self.failure_count = 0
            
            return result
            
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            logger.warning(f"Circuit breaker: Failure {self.failure_count}/{self.failure_threshold}")
            
            # Open circuit if threshold reached
            if self.failure_count >= self.failure_threshold:
                logger.error(f"Circuit breaker: OPEN (threshold reached)")
                self.state = 'OPEN'
            
            raise


class ErrorRecovery:
    """
    Error recovery utilities for production
    """
    
    @staticmethod
    def safe_execute(func: Callable,
                    default_value: Any = None,
                    log_error: bool = True) -> Any:
        """
        Execute function safely with error handling
        
        Args:
            func: Function to execute
            default_value: Value to return on error
            log_error: Whether to log errors
            
        Returns:
            Function result or default value on error
        """
        try:
            return func()
        except Exception as e:
            if log_error:
                logger.error(f"Error in {func.__name__}: {e}")
            return default_value
    
    @staticmethod
    def log_exception(func: Callable) -> Callable:
        """
        Decorator to log exceptions with full traceback
        
        Usage:
            @ErrorRecovery.log_exception
            def my_function():
                pass
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Exception in {func.__name__}: {e}", exc_info=True)
                raise
        
        return wrapper
    
    @staticmethod
    def graceful_shutdown(cleanup_funcs: list):
        """
        Graceful shutdown with cleanup
        
        Args:
            cleanup_funcs: List of cleanup functions to call
        """
        logger.info("🛑 Initiating graceful shutdown...")
        
        for func in cleanup_funcs:
            try:
                logger.info(f"Cleaning up: {func.__name__}")
                func()
            except Exception as e:
                logger.error(f"Error during cleanup ({func.__name__}): {e}")
        
        logger.info("✅ Shutdown complete")


# Network error handling
class NetworkErrorHandler:
    """Handle network-related errors"""
    
    NETWORK_EXCEPTIONS = (
        ConnectionError,
        TimeoutError,
        OSError,
    )
    
    @staticmethod
    def is_network_error(exception: Exception) -> bool:
        """Check if exception is network-related"""
        return isinstance(exception, NetworkErrorHandler.NETWORK_EXCEPTIONS)
    
    @staticmethod
    def retry_on_network_error(max_attempts: int = 3):
        """Decorator to retry on network errors"""
        return retry_on_error(
            config=RetryConfig(max_attempts=max_attempts),
            exceptions=NetworkErrorHandler.NETWORK_EXCEPTIONS
        )


if __name__ == "__main__":
    # Test error recovery
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("ERROR RECOVERY TEST")
    print("="*70)
    
    # Test 1: Retry decorator
    print("\n🧪 Test 1: Retry on error")
    
    attempt_count = 0
    
    @retry_on_error(config=RetryConfig(max_attempts=3, initial_delay=0.5))
    def flaky_function():
        global attempt_count
        attempt_count += 1
        
        if attempt_count < 3:
            raise ConnectionError(f"Network error (attempt {attempt_count})")
        
        return "Success!"
    
    try:
        result = flaky_function()
        print(f"✅ Result: {result}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 2: Circuit breaker
    print("\n🧪 Test 2: Circuit breaker")
    
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=2.0)
    
    def unreliable_service():
        raise ConnectionError("Service unavailable")
    
    # Trigger failures
    for i in range(5):
        try:
            breaker.call(unreliable_service)
        except Exception as e:
            print(f"Attempt {i+1}: {e}")
    
    # Test 3: Safe execute
    print("\n🧪 Test 3: Safe execute")
    
    def risky_function():
        raise ValueError("Something went wrong")
    
    result = ErrorRecovery.safe_execute(
        lambda: risky_function(),
        default_value="Default value"
    )
    print(f"✅ Safe result: {result}")
    
    print("\n✅ All tests completed!")
