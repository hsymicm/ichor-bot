import os
from cryptography.fernet import Fernet
import json

key1 = os.getenv("decrypt")
fernet = Fernet(key1)

def save(filename, dictionary):
  with open(filename, "w") as output:
    json.dump(dictionary, output, indent=4, sort_keys=True)

  with open(filename, 'rb') as dec:
    decrypted = dec.read()

  encrypted = fernet.encrypt(decrypted)

  with open(filename, 'wb') as enc:
    enc.write(encrypted)

def load(filename):
  with open(filename, 'rb') as enc:
    encrypted = enc.read()

  decrypted = fernet.decrypt(encrypted)

  with open(filename, 'wb') as dec:
    dec.write(decrypted)

  return json.load(open(filename))