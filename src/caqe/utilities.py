#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utility functions
"""
import base64
import json

from itsdangerous import URLSafeSerializer
from Crypto.Cipher import AES

from caqe import app

def sign_data(data):
    """
    Serialize and sign data (likely to be put in a session cookie).
    Parameters
    ----------
    data : object
        Data to be serialized and signed.
    Returns
    -------
    str
        Encrypted data
    """
    s = URLSafeSerializer(app.secret_key)
    return s.dumps(data)


def unsign_data(signed_data):
    """
    Unsign and unserialize signed data
    Parameters
    ----------
    signed_data : str
        The signed and serialized data
    Returns
    -------
    object
        Decrypted data
    """
    s = URLSafeSerializer(app.secret_key)
    return s.loads(signed_data)


def encrypt_data(data):
    """
    Serialize and encrypt data (likely to be put in a session cookie).

    Parameters
    ----------
    data : object
        Data to be serialized and encrypted.

    Returns
    -------
    str
        Encrypted data
    """
    datas = json.dumps(data)

    # pad with '{'
    datas += (AES.block_size - len(datas) % AES.block_size) * '{'
    aes = AES.new(app.secret_key)
    return base64.urlsafe_b64encode(aes.encrypt(datas))


def decrypt_data(encrypted_data):
    """
    Decrypt and unserialize encrypted data

    Parameters
    ----------
    encrypted_data : str
        The encrypted and serialized data

    Returns
    -------
    object : object
        Decrypted data
    """
    aes = AES.new(app.secret_key)
    datas = aes.decrypt(base64.urlsafe_b64decode(encrypted_data))

    # remove padding '{'
    datas = datas.rstrip('{')
    data = json.loads(datas)
    return data
