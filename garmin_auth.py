#!/usr/bin/env python3
"""
This script authenticates with Garmin using the Garth library,
then saves the tokens in the format expected by the C# RenphoGarminSync application.
"""
import garth
import json
import os
import base64
from datetime import datetime
from getpass import getpass
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# AES encryption to match C# implementation
ENCRYPTION_KEY = "p13aSeD0ntSteaL0"


def aes_encrypt(plaintext, key):
    """Encrypt using AES ECB mode to match C# AesUtility"""
    # Convert key to bytes (UTF-8 encoding, exactly 16 bytes)
    key_bytes = key.encode("utf-8")

    # Create cipher in ECB mode (as used in C# code)
    cipher = AES.new(key_bytes, AES.MODE_ECB)

    # Pad and encrypt (PKCS7 padding)
    padded_data = pad(plaintext.encode("utf-8"), AES.block_size)
    encrypted = cipher.encrypt(padded_data)

    # Return base64 encoded
    return base64.b64encode(encrypted).decode("utf-8")


def escape_path(username):
    """Escape username for filesystem path (simple version)"""
    # Replace characters that might be problematic in paths
    return username.replace("/", "_").replace("\\", "_").replace(":", "_")


def save_tokens_for_csharp(email, oauth1_token, oauth2_token):
    """Save tokens in C# app format"""
    # Create the auth entry structure
    auth_entry = {
        "Username": email,
        "Stage": 2,  # AuthStage.Completed
        "OAuth1Token": {
            "Token": oauth1_token.oauth_token,
            "TokenSecret": oauth1_token.oauth_token_secret,
            "IssuedAt": datetime.utcnow().isoformat() + "Z",
        },
        "OAuth2Token": {
            "scope": oauth2_token.scope,
            "jti": oauth2_token.jti,
            "token_type": oauth2_token.token_type,
            "access_token": oauth2_token.access_token,
            "refresh_token": oauth2_token.refresh_token,
            "expires_in": oauth2_token.expires_in,
            "refresh_token_expires_in": oauth2_token.refresh_token_expires_in,
            "IssuedAt": datetime.utcnow().isoformat() + "Z",
        },
        "MFAState": None,
    }

    # Serialize to JSON
    json_str = json.dumps(auth_entry)

    # Encrypt
    encrypted = aes_encrypt(json_str, ENCRYPTION_KEY)

    # Save to file
    base_path = os.path.expanduser("~/Documents/RenphoGarminSync")
    escaped_username = escape_path(email)
    dir_path = os.path.join(base_path, "GarminAuth", escaped_username)

    # Create directory
    os.makedirs(dir_path, exist_ok=True)

    # Write encrypted state
    state_file = os.path.join(dir_path, "state.json")
    with open(state_file, "w") as f:
        f.write(encrypted)

    print(f"✓ Tokens saved to: {state_file}")
    return state_file


def main():
    email = input("Enter Garmin email: ")
    password = getpass("Enter Garmin password: ")

    try:
        # Authenticate with Garmin
        print("\nAuthenticating with Garmin...")
        garth.login(email, password)
        print("✓ Login successful!")

        # Get tokens
        oauth1 = garth.client.oauth1_token
        oauth2 = garth.client.oauth2_token

        print(f"\n✓ OAuth1 Token: {oauth1.oauth_token[:20]}...")
        print(f"✓ OAuth2 Access Token: {oauth2.access_token[:20]}...")

        # Save for C# app
        print("\nSaving tokens for C# application...")
        state_file = save_tokens_for_csharp(email, oauth1, oauth2)

        print("\n" + "=" * 60)
        print("SUCCESS! You can now use the C# application:")
        print("=" * 60)
        print(
            f"\nrgs sync --gu {email} --ru <renpho_email> --rpw <renpho_password>\n"
        )

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
