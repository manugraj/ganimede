import base64
import hashlib
import uuid
from random import Random

from Crypto.Cipher import AES


def to_hash_argon2(data):
    from argon2 import PasswordHasher
    return PasswordHasher().hash(data)


def unique(size: int):
    return uuid.uuid4().hex[:size].upper()


class CrypticTalk:

    @staticmethod
    def def_encrypt(message):
        message = CrypticTalk._pad(message, 16)
        iv = 'Austral0P1thecus'
        cipher = AES.new("We're 3.14x more", AES.MODE_CBC, iv)
        return (base64.b64encode(iv.encode() + cipher.encrypt(message.encode()))).decode('utf-8')

    @staticmethod
    def def_decrypt(ciphertext):
        enc = base64.b64decode(ciphertext)
        iv = 'Austral0P1thecus'
        cipher = AES.new("We're 3.14x more", AES.MODE_CBC, iv)
        return CrypticTalk._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = CrypticTalk._pad(raw, self.bs)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return CrypticTalk._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    @staticmethod
    def _pad(s, bs):
        return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]
