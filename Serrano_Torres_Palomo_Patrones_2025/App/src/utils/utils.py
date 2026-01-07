def is_prime(n):
    """Return True if ``n`` is a prime number, False otherwise.

    Parameters
    - n: integer to test for primality

    The implementation uses simple deterministic checks suitable for
    small integers: special-cases 0,1,2, filters even numbers and tests odd
    divisors up to sqrt(n). This function is intentionally simple and
    optimized for readability rather than large-number performance.
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    return True
