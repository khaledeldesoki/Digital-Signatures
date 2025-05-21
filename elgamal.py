import random
import hashlib

def is_prime(n):
    """Check if a number is prime."""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def mod_inverse(a, m):
    """Calculate the modular multiplicative inverse of a modulo m."""
    g, x, y = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    else:
        return x % m

def extended_gcd(a, b):
    """Extended Euclidean Algorithm to find gcd(a, b) and coefficients x, y such that ax + by = gcd(a, b)."""
    if a == 0:
        return b, 0, 1
    else:
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    2   
def generate_keys(p, g, x):
    """
    Generate ElGamal keys.
    p: prime number
    g: generator (primitive root modulo p)
    x: private key (random number < p)
    Returns: public key y = g^x mod p
    """
    y = pow(g, x, p)
    return y

def hash_message(message):
    """Hash the message using SHA-256."""
    hash_obj = hashlib.sha256(message.encode())
    # Convert the hash to an integer
    return int(hash_obj.hexdigest(), 16)

def sign_message(message, p, g, x, k):
    """
    Sign a message using ElGamal signature scheme.
    message: the message to sign
    p: prime number
    g: generator
    x: private key
    k: random number that is relatively prime to p-1
    Returns: signature (r, s)
    """
    # Hash the message
    h = hash_message(message)
    
    # Calculate r = g^k mod p
    r = pow(g, k, p)
    
    # Calculate s = (h - x*r) * k^(-1) mod (p-1)
    k_inv = mod_inverse(k, p-1)
    s = (k_inv * (h - x * r)) % (p-1)
    
    return r, s

def verify_signature(message, r, s, p, g, y):
    """
    Verify ElGamal signature.
    message: the signed message
    r, s: signature
    p: prime number
    g: generator
    y: public key
    Returns: True if signature is valid, False otherwise
    """
    # Check if r is in [1, p-1]
    if r <= 0 or r >= p:
        return False
    
    # Hash the message
    h = hash_message(message)
    
    # Calculate v1 = g^h mod p
    v1 = pow(g, h, p)
    
    # Calculate v2 = y^r * r^s mod p
    v2 = (pow(y, r, p) * pow(r, s, p)) % p
    
    return v1 == v2

def main():
    print("=" * 50)
    print("ElGamal Digital Signature Scheme")
    print("=" * 50)
    
    # Get user input for prime number p
    while True:
        try:
            p = int(input("Enter a prime number p: "))
            if not is_prime(p):
                print("Error: The number must be prime. Please try again.")
                continue
            break
        except ValueError:
            print("Error: Please enter a valid integer.")
    
    # Get user input for generator g
    while True:
        try:
            g = int(input(f"Enter a generator g (1 < g < {p}): "))
            if g <= 1 or g >= p:
                print(f"Error: g must be between 1 and {p}. Please try again.")
                continue
            break
        except ValueError:
            print("Error: Please enter a valid integer.")
    
    # Get user input for private key x
    while True:
        try:
            x = int(input(f"Enter a private key x (1 < x < {p-1}): "))
            if x <= 1 or x >= p-1:
                print(f"Error: x must be between 1 and {p-2}. Please try again.")
                continue
            break
        except ValueError:
            print("Error: Please enter a valid integer.")
    
    # Generate public key y
    y = generate_keys(p, g, x)
    print(f"Public key y = {y}")
    
    # Get message from user
    message = input("Enter the message to sign: ")
    
    # Get random k for signing
    while True:
        try:
            k = int(input(f"Enter a random k (1 < k < {p-1} and gcd(k, {p-1}) = 1): "))
            if k <= 1 or k >= p-1:
                print(f"Error: k must be between 1 and {p-2}. Please try again.")
                continue
            
            # Check if k is relatively prime to p-1
            if extended_gcd(k, p-1)[0] != 1:
                print(f"Error: k must be relatively prime to {p-1}. Please try again.")
                continue
            
            break
        except ValueError:
            print("Error: Please enter a valid integer.")
    
    # Sign the message
    r, s = sign_message(message, p, g, x, k)
    print(f"Signature: r = {r}, s = {s}")
    
    # Verify the signature
    valid = verify_signature(message, r, s, p, g, y)
    print(f"Signature verification: {'Valid' if valid else 'Invalid'}")

if __name__ == "__main__":
    main()
