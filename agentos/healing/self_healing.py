"""
AgentOS Self-Healing System

Multi-layer self-healing:
- Retry with exponential backoff + jitter
- Circuit breaker at 3 failures
- Stale data detection
- Process restart on crash
- Graceful degradation
"""

import time
import random
from typing import Optional, Callable, Any, Dict, List
from enum import Enum


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 10,
        base_delay_ms: int = 500,
        max_delay_ms: int = 300000,
        jitter_factor: float = 0.1,
        exponential_base: float = 2.0,
    ):
        self.max_retries = max_retries
        self.base_delay_ms = base_delay_ms
        self.max_delay_ms = max_delay_ms
        self.jitter_factor = jitter_factor
        self.exponential_base = exponential_base


class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout_ms: int = 60000,
        half_open_max_calls: int = 1,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_ms = recovery_timeout_ms
        self.half_open_max_calls = half_open_max_calls


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker to prevent cascade failures."""

    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        self.config = config or CircuitBreakerConfig()
        self.failure_count: int = 0
        self.last_failure_time: Optional[float] = None
        self.state: CircuitState = CircuitState.CLOSED
        self.half_open_calls: int = 0

    def record_success(self) -> None:
        """Record a successful call."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.half_open_calls = 0

    def record_failure(self) -> None:
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN

    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if self.last_failure_time is None:
                return True
            elapsed_ms = (time.time() - self.last_failure_time) * 1000
            if elapsed_ms >= self.config.recovery_timeout_ms:
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls < self.config.half_open_max_calls:
                self.half_open_calls += 1
                return True
            return False

        return False

    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "half_open_calls": self.half_open_calls,
        }


def retry_with_backoff(
    func: Callable,
    config: Optional[RetryConfig] = None,
    retryable_exceptions: Optional[List[type]] = None,
) -> Any:
    """Execute function with retry and exponential backoff + jitter."""
    config = config or RetryConfig()
    retryable_exceptions = retryable_exceptions or [Exception]

    last_exception: Optional[Exception] = None
    for attempt in range(config.max_retries + 1):
        try:
            return func()
        except Exception as e:
            if retryable_exceptions and not any(
                isinstance(e, exc) for exc in retryable_exceptions
            ):
                raise
            last_exception = e
            if attempt == config.max_retries:
                break

            # Calculate delay with exponential backoff
            delay_ms = config.base_delay_ms * (config.exponential_base**attempt)
            delay_ms = min(delay_ms, config.max_delay_ms)

            # Add jitter
            jitter = delay_ms * config.jitter_factor * (random.random() * 2 - 1)
            delay_ms = max(0, delay_ms + jitter)

            time.sleep(delay_ms / 1000.0)

    if last_exception:
        raise last_exception
    raise RuntimeError("Retry loop exited without exception or result")


class SelfHealingSystem:
    """Coordinates all self-healing mechanisms."""

    def __init__(
        self,
        retry_config: Optional[RetryConfig] = None,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
    ):
        self.retry_config = retry_config or RetryConfig()
        self.circuit_breaker_config = circuit_breaker_config or CircuitBreakerConfig()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

    def get_circuit_breaker(self, name: str) -> CircuitBreaker:
        """Get or create a circuit breaker by name."""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(self.circuit_breaker_config)
        return self.circuit_breakers[name]

    def execute_with_healing(
        self,
        name: str,
        func: Callable,
        fallback: Optional[Callable] = None,
        retryable_exceptions: Optional[List[type]] = None,
    ) -> Any:
        """Execute function with full self-healing support."""
        cb = self.get_circuit_breaker(name)

        if not cb.can_execute():
            if fallback:
                return fallback()
            raise RuntimeError(f"Circuit breaker open for {name}")

        try:
            result = retry_with_backoff(func, self.retry_config, retryable_exceptions)
            cb.record_success()
            return result
        except Exception as e:
            cb.record_failure()
            if fallback:
                return fallback()
            raise
