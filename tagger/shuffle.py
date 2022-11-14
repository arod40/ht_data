"Got from: https://chrismaclellan.com/blog/lazy-shuffled-list-generator"
"Used: Multiplicative Congruential Generator"

from random import randint

def lazy_shuffle(start, stop=None, step=1):
    """
    This generates the full range and shuffles it using a Lehmer random number
    generator, which is also called a multiplicative congruential generator and
    is a special case of a linear congruential generator:
        <a href="https://en.wikipedia.org/wiki/Lehmer_random_number_generator" target="_blank">https://en.wikipedia.org/wiki/Lehmer_random_number_generator</a>
        <a href="https://en.wikipedia.org/wiki/Linear_congruential_generator" target="_blank">https://en.wikipedia.org/wiki/Linear_congruential_generator</a>
    Basically, we are iterating through the elements in a finite field. There
    are a few complications. First, we select a prime modulus that is slightly
    larger than the size of the range. Then, if we get elements outside the
    range we ignore them and continue iterating. Finally, we need the generator
    to be a primitive root of the selected modulus, so that we generate a full
    cycle. The seed provides most of the randomness of the permutation,
    although we also randomly select a primitive root.
    This function has the same args as the builtin ``range'' function, but
    returns the values in shuffled order:
        range(stop)
        range(start, stop[, step])
    >>> sorted([i for i in lazyshuffledrange2(10)])
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> sorted([i for i in lazyshuffledrange2(2, 20, 3)])
    [2, 5, 8, 11, 14, 17]
    """
    if stop is None:
        stop = start
        start = 0
    l = (stop - start) // step
    m = nextPrime(l)
    a = randint(2, m - 1)
    while not isPrimitiveRoot(a, m):
        a = randint(2, m - 1)
    seed = randint(1, l - 1)
    x = seed
    while True:
        if x <= l:
            yield step * (x - 1) + start
        x = (a * x) % m
        if x == seed:
            break


def nextPrime(n):
    p = n + 1
    if p <= 2:
        return 2
    if p % 2 == 0:
        p += 1
    while not isPrime(p):
        p += 2
    return p


def isPrime(n):
    if n <= 1:
        return False
    elif n <= 3:
        return True
    elif n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def isPrimitiveRoot(a, n):
    # assuming n is prime then eulers totient = n-1
    phi = n - 1
    for p in factorize(phi):
        if pow(a, phi // p, n) == 1:
            return False
    return True


def factorize(n):
    """
    A naive approach to finding the prime factors of a number n.
    >>> [i for i in factorize(10)]
    [2, 5]
    >>> [i for i in factorize(7*11*13)]
    [7, 11, 13]
    >>> [i for i in factorize(101 * 211)]
    [101, 211]
    >>> [i for i in factorize(11*13)]
    [11, 13]
    """
    if n <= 3:
        raise StopIteration
    i = 2
    step = 1
    last = 0
    while i * i <= n:
        while n > 1:
            while n % i == 0:
                if i > last:
                    yield i
                    last = i
                n //= i
            i += step
            step = 2
