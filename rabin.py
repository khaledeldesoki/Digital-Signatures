import hashlib
import random
from sympy import isprime, mod_inverse, nextprime

def hash_message(message):
    """Hash the message using SHA-256 and return an integer."""
    h = hashlib.sha256(message.encode('utf-8')).hexdigest()
    return int(h, 16)

def generate_prime(bits=512):
    """Generate a prime number of specified bit length."""
    p = random.getrandbits(bits)
    while not (p % 4 == 3 and isprime(p)):
        p = nextprime(p)
    return p

def key_generation(bits=512):
    """Generate Rabin key pair."""
    p = generate_prime(bits)
    q = generate_prime(bits)
    n = p * q
    return (n, p, q)

def sign(message, p, q):
    """Generate a Rabin signature."""
    n = p * q
    m = hash_message(message) % n

    # Find square roots modulo p and q
    r_p = pow(m, (p + 1) // 4, p)
    r_q = pow(m, (q + 1) // 4, q)

    # Apply Chinese Remainder Theorem to combine roots
    inv_q = mod_inverse(q, p)
    x = (r_q + q * ((inv_q * (r_p - r_q)) % p)) % n

    # Select the smallest root as canonical signature
    signature = min(x, n - x)
    return signature

def verify(message, signature, n):
    """Verify a Rabin signature."""
    m = hash_message(message) % n
    check = pow(signature, 2, n)
    print(f"[DEBUG] Hashed message mod n: {m}")
    print(f"[DEBUG] Signature² mod n: {check}")
    # Check if either the signature or its negative (mod n) matches
    return check == m or (n - check) == m

def get_valid_prime(prompt):
    """Get a valid prime number from user input."""
    while True:
        try:
            p = int(input(prompt))
            if not isprime(p):
                print("❌ Not a prime. Try again.")
            elif p % 4 != 3:
                print("❌ Prime must be congruent to 3 mod 4. Try again.")
            else:
                return p
        except ValueError:
            print("❌ Invalid input. Enter an integer.")

def key_generation_manual():
    """Generate Rabin key pair with user input."""
    print("Enter two primes p and q such that p ≡ q ≡ 3 mod 4:")
    p = get_valid_prime("Enter prime p: ")
    q = get_valid_prime("Enter prime q: ")
    n = p * q
    print("✅ Key generation complete.")
    print("Public key n =", n)
    return n, p, q

if __name__ == "__main__":
    print("=== Rabin Digital Signature Scheme ===")
    
    while True:
        print("\n1. Generate Keys")
        print("2. Sign Message")
        print("3. Verify Signature")
        print("4. Exit")
        choice = input("Choose an option (1/2/3/4): ")

        if choice == '1':
            n, p, q = key_generation_manual()
            print("Private keys (p, q) =", (p, q))
            print("Public key n =", n)

        elif choice == '2':
            if 'n' not in locals():
                print("❌ Please generate keys first (Option 1)")
                continue
            msg = input("Enter the message to sign: ")
            sig = sign(msg, p, q)
            print("🖋️ Signature:", sig)

        elif choice == '3':
            if 'n' not in locals():
                print("❌ Please generate keys first (Option 1)")
                continue
            msg = input("Enter the original message: ")
            try:
                sig = int(input("Enter the signature: "))
                result = verify(msg, sig, n)
                print("✅ Valid Signature." if result else "❌ Invalid Signature.")
            except ValueError:
                print("❌ Signature must be an integer.")

        elif choice == '4':
            print("Exiting.")
            break
        else:
            print("❌ Invalid option. Try again.")
