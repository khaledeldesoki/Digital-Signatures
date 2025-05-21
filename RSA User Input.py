from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateNumbers, RSAPublicNumbers
import sympy
mas_input = input("enter message = ")
message = mas_input.encode()
p = int(input("enter prime number p = "))
q = int(input("enter prime number q = "))

if not sympy.isprime(p) or not sympy.isprime(q):
    print("Both p and q must be prime numbers!")
    exit()

n = p * q
phi = (p - 1) * (q - 1)
e = 65537

if sympy.gcd(e, phi) != 1:
    print("e and phi(n) are not coprime")
    exit()
d = pow(e, -1, phi)

dmp1 = d % (p - 1)
dmq1 = d % (q - 1)
iqmp = pow(q, -1, p)
public_numbers = RSAPublicNumbers(e, n)
private_numbers = RSAPrivateNumbers(p=p,q=q,d=d,dmp1=dmp1,
    dmq1=dmq1,
    iqmp=iqmp,
    public_numbers=public_numbers)

private_key = private_numbers.private_key(default_backend())
public_key = private_key.public_key()

print("key generation done")
print("prime p =", p)
print("prime q =", q)
print("RSA modulus n =", n)
print("private exponent d =", d)
print("public exponent e =", e)

def sign(message, private_key):
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("Signing done")
    return signature

def verify(message, signature, public_key):
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("Signature is valid")
        return True
    except InvalidSignature:
        print("Invalid signature!")

# التوقيع والتحقق
signature = sign(message, private_key)
signing = int.from_bytes(signature, byteorder='big')
print("Signature as int =", signing)
verify(message, signature, public_key)