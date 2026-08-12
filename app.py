import json
import sys
import base64
from typing import Optional, Tuple

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# ---------- AES / encryption (from follow_cap.py) ----------
_gAyKeY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
_gAyIv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

def _sHuFfLeShIt(dAtA: bytes) -> bytes:
    cIpHeR = AES.new(_gAyKeY, AES.MODE_CBC, _gAyIv)
    return cIpHeR.encrypt(pad(dAtA, AES.block_size))

# ---------- JWT fetch ----------
def _gEtMyJwT(uId: int, pAsSwOrD: str) -> Optional[str]:
    pArAmS = {
        "guest_uid": str(uId),
        "guest_password": pAsSwOrD
    }
    try:
        rEsP = requests.get("https://ff-jwt-gen-api.lovable.app/api/public/token",
                            params=pArAmS, timeout=15)
        rEsP.raise_for_status()
        dAtA = rEsP.json()
        if dAtA.get("success") and dAtA.get("token"):
            return dAtA.get("token")
        return None
    except Exception:
        return None

# ---------- Fixed request data ----------
REQUEST_HEX = "1A 72 5B 2C 56 EC 52 BA 7D 09 62 34 54 C0 A0 03"
REQUEST_BYTES = bytes.fromhex(REQUEST_HEX.replace(" ", ""))

URL = "https://client.ind.freefiremobile.com/GetFollowedCreatorStats"

# ---------- Protobuf parser ----------
def decode_varint(data: bytes, offset: int) -> Tuple[int, int]:
    result = 0
    shift = 0
    while True:
        if offset >= len(data):
            raise ValueError("Unexpected end of data while reading varint")
        byte = data[offset]
        offset += 1
        result |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            break
        shift += 7
    return result, offset

def count_repeated_field_1(data: bytes) -> int:
    count = 0
    offset = 0
    while offset < len(data):
        key, offset = decode_varint(data, offset)
        num = key >> 3
        wire = key & 0x07
        if wire == 0:
            _, offset = decode_varint(data, offset)
        elif wire == 1:
            offset += 8
        elif wire == 2:
            length, offset = decode_varint(data, offset)
            offset += length
            if num == 1:
                count += 1
        elif wire == 5:
            offset += 4
        # ignore groups
    return count

# ---------- Main handler ----------
def handler(request):
    """
    Vercel serverless function entry point.
    Expects query parameters: uid (int) and password (str)
    """
    # Get query parameters
    uid_str = request.args.get("uid")
    password = request.args.get("password")
    if not uid_str or not password:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing uid or password"})
        }
    try:
        uid = int(uid_str)
    except ValueError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "uid must be an integer"})
        }

    # Step 1: Obtain JWT
    jwt = _gEtMyJwT(uid, password)
    if not jwt:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Failed to obtain JWT"})
        }

    # Step 2: Build headers (same as follow_cap.py)
    headers = {
        "Authorization": f"Bearer {jwt}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "deflate, gzip",
        "Releaseversion": "OB54",
        "User-Agent": "UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
        "Accept": "*/*",
        "X-Unity-Version": "2022.3.47f1",
        "X-Ga": "v1 1",
    }

    # Step 3: Send fixed request
    try:
        resp = requests.post(URL, data=REQUEST_BYTES, headers=headers, timeout=15)
        if resp.status_code != 200:
            return {
                "statusCode": 502,
                "body": json.dumps({"error": f"Upstream HTTP {resp.status_code}"})
            }
        total = count_repeated_field_1(resp.content)
        remains = 50 - total
        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "followed": total,
                "remains": remains
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
