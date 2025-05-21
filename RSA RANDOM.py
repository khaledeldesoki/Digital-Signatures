from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
mes_input = input("enter message = ")
message = mes_input.encode()
def key_gen():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    print("key generation don")
    return private_key, public_key

def sign(message, private_key):
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("signing don")
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
        print("signature is valid")
        return True
    except InvalidSignature:
        print("signature is invalid")

private_key, public_key = key_gen()
private_num=private_key.private_numbers()
public_num=private_num.public_numbers
n=public_num.n
print("prime p = ",private_num.p)
print("prime q = ",private_num.q)
print("RSA modulus n = ",n)
print("private exponent d = " ,private_num.d)
print("public exponent e = ",public_num.e)
signature = sign(message, private_key)
signing=int.from_bytes(signature , byteorder='big')
print("signature as int = ",signing )
verify(message, signature, public_key)