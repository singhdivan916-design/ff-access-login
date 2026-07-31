# ============================================================
# SELF-CONTAINED TELEGRAM BOT – 100% ORIGINAL LOGIC
# ============================================================

import os, sys, time, json, base64, binascii, uuid
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")
import requests
requests.packages.urllib3.disable_warnings()
from flask import Flask, request, Response
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from google.protobuf import descriptor_pool, message_factory
import blackboxprotobuf
from supabase import create_client, Client

# ---------- 🔴 EDIT THESE TWO WITH YOUR CREDENTIALS ----------
TELEGRAM_BOT_TOKEN = "8805719889:AAG-ospZfYhBWfKfEX4sHbfl-b4LEyNJVPc"          # <-- Replace
SUPABASE_URL = "https://qiotvvqlgajwvfcegnbz.supabase.co"
SUPABASE_KEY = "sb_secret_ssmz9sOSczbXj1S1qlFFYw_DpM2zu5G"
WEBHOOK_BASE = "https://ff-access-login.vercel.app"       # <-- Replace
TABLE_NAME = "ff_bot_users"   # keep as is
# -----------------------------------------------------------

if not all([TELEGRAM_BOT_TOKEN, SUPABASE_URL, SUPABASE_KEY, WEBHOOK_BASE]):
    raise RuntimeError("Please fill in TELEGRAM_BOT_TOKEN and WEBHOOK_BASE in the script.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------- EXACT ORIGINAL VARIABLES & FUNCTIONS ----------
mYdEsCrIpToR = b'\n\x08my.proto"\xae\t\n\x08GameData\x12\x11\n\ttimestamp\x18\x03 \x01(\t\x12\x11\n\tgame_name\x18\x04 \x01(\t\x12\x14\n\x0cgame_version\x18\x05 \x01(\x05\x12\x14\n\x0cversion_code\x18\x07 \x01(\t\x12\x0f\n\x07os_info\x18\x08 \x01(\t\x12\x13\n\x0bdevice_type\x18\t \x01(\t\x12\x18\n\x10network_provider\x18\n \x01(\t\x12\x17\n\x0fconnection_type\x18\x0b \x01(\t\x12\x14\n\x0cscreen_width\x18\x0c \x01(\x05\x12\x15\n\rscreen_height\x18\r \x01(\x05\x12\x0b\n\x03dpi\x18\x0e \x01(\t\x12\x10\n\x08cpu_info\x18\x0f \x01(\t\x12\x11\n\ttotal_ram\x18\x10 \x01(\x05\x12\x10\n\x08gpu_name\x18\x11 \x01(\t\x12\x13\n\x0bgpu_version\x18\x12 \x01(\t\x12\x0f\n\x07user_id\x18\x13 \x01(\t\x12\x12\n\nip_address\x18\x14 \x01(\t\x12\x10\n\x08language\x18\x15 \x01(\t\x12\x0f\n\x07open_id\x18\x16 \x01(\t\x12\x15\n\rplatform_type\x18\x17 \x01(\x05\x12\x1a\n\x12device_form_factor\x18\x18 \x01(\t\x12\x14\n\x0cdevice_model\x18\x19 \x01(\t\x12\x14\n\x0caccess_token\x18\x1d \x01(\t\x12\x18\n\x10unknown_field_30\x18\x1e \x01(\x05\x12"\n\x1asecondary_network_provider\x18) \x01(\t\x12!\n\x19secondary_connection_type\x18* \x01(\t\x12\x11\n\tunique_id\x18\x39 \x01(\t\x12\x10\n\x08field_60\x18< \x01(\x05\x12\x10\n\x08field_61\x18= \x01(\x05\x12\x10\n\x08field_62\x18> \x01(\x05\x12\x10\n\x08field_63\x18? \x01(\x05\x12\x10\n\x08field_64\x18@ \x01(\x05\x12\x10\n\x08field_65\x18A \x01(\x05\x12\x10\n\x08field_66\x18B \x01(\x05\x12\x10\n\x08field_67\x18C \x01(\x05\x12\x10\n\x08field_70\x18F \x01(\x05\x12\x10\n\x08field_73\x18I \x01(\x05\x12\x14\n\x0clibrary_path\x18J \x01(\t\x12\x10\n\x08field_76\x18L \x01(\x05\x12\x10\n\x08apk_info\x18M \x01(\t\x12\x10\n\x08field_78\x18N \x01(\x05\x12\x10\n\x08field_79\x18O \x01(\x05\x12\x17\n\x0fos_architecture\x18Q \x01(\t\x12\x14\n\x0cbuild_number\x18S \x01(\t\x12\x10\n\x08field_85\x18U \x01(\x05\x12\x18\n\x10graphics_backend\x18V \x01(\t\x12\x19\n\x11max_texture_units\x18W \x01(\x05\x12\x15\n\rrendering_api\x18X \x01(\x05\x12\x18\n\x10encoded_field_89\x18Y \x01(\t\x12\x10\n\x08field_92\x18\\ \x01(\x05\x12\x13\n\x0bmarketplace\x18] \x01(\t\x12\x16\n\x0eencryption_key\x18^ \x01(\t\x12\x15\n\rtotal_storage\x18_ \x01(\x05\x12\x10\n\x08field_97\x18a \x01(\x05\x12\x10\n\x08field_98\x18b \x01(\x05\x12\x10\n\x08field_99\x18c \x01(\t\x12\x11\n\tfield_100\x18d \x01(\tb\x06proto3'

oUtPuTdEsCrIpToR = b'\n\x13jwt_generator.proto"\xd2\x02\n\nGarena_420\x12\x12\n\naccount_id\x18\x01 \x01(\x03\x12\x0e\n\x06region\x18\x02 \x01(\t\x12\r\n\x05place\x18\x03 \x01(\t\x12\x10\n\x08location\x18\x04 \x01(\t\x12\x0e\n\x06status\x18\x05 \x01(\t\x12\r\n\x05token\x18\x08 \x01(\t\x12\n\n\x02id\x18\t \x01(\x05\x12\x0b\n\x03api\x18\n \x01(\t\x12\x0e\n\x06number\x18\x0c \x01(\x05\x12\x1e\n\tGarena420\x18\x0f \x01(\x0b\x32\x0b.Garena_420\x12\x0c\n\x04area\x18\x10 \x01(\t\x12\x11\n\tmain_area\x18\x12 \x01(\t\x12\x0c\n\x04city\x18\x13 \x01(\t\x12\x0c\n\x04name\x18\x14 \x01(\t\x12\x11\n\ttimestamp\x18\x15 \x01(\x03\x12\x0e\n\x06binary\x18\x16 \x01(\x0c\x12\x13\n\x0bbinary_data\x18\x17 \x01(\x0c\x1a"\n\x12Decrypted_Payloads\x12\x0c\n\x04type\x18\x01 \x01(\x05b\x06proto3'

pOoL = descriptor_pool.Default()
pOoL.AddSerializedFile(mYdEsCrIpToR)
pOoL.AddSerializedFile(oUtPuTdEsCrIpToR)

gAmEdAtA = message_factory.GetMessageClass(pOoL.FindMessageTypeByName('GameData'))
gArEnA420 = message_factory.GetMessageClass(pOoL.FindMessageTypeByName('Garena_420'))

aEsKeY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
aEsIv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

mAjOrLoGiNuRl = "https://loginbp.ggblueshark.com/MajorLogin"
iNsPeCtUrL = "https://100067.connect.garena.com/oauth/token/inspect"

def eNcRyPtDaTa(dAtA):
    cIpHeR = AES.new(aEsKeY, AES.MODE_CBC, aEsIv)
    return cIpHeR.encrypt(pad(dAtA, AES.block_size))

def dEcRyPtDaTa(dAtA):
    if len(dAtA) % 16 != 0:
        return dAtA
    try:
        cIpHeR = AES.new(aEsKeY, AES.MODE_CBC, aEsIv)
        return unpad(cIpHeR.decrypt(dAtA), AES.block_size)
    except:
        return dAtA

def pRoToBuFdEcOdE(dAtA: bytes):
    dEcOdEd, _ = blackboxprotobuf.decode_message(dAtA)
    return dEcOdEd

def iNsPeCtToKeN(aCcEsStOkEn):
    uRl = f"{iNsPeCtUrL}?token={aCcEsStOkEn}"
    hEaDeRs = {'User-Agent': "GarenaMSDK/4.0.19P9"}
    rEsP = requests.get(uRl, headers=hEaDeRs, timeout=10, verify=False)
    if rEsP.status_code != 200:
        raise Exception(f"Inspect failed: {rEsP.status_code}")
    dAtA = rEsP.json()
    return dAtA.get('open_id')

xOrKeY = b"1e5898ccb8dfdd921f9bdea848768b64a201"

def dEcOdEfFnAmE(b64_str: str) -> str:
    try:
        if not b64_str:
            return ""
        b64_str = b64_str.strip()
        b64_str += "=" * ((4 - len(b64_str) % 4) % 4)
        encrypted_bytes = base64.b64decode(b64_str)
        decrypted_bytes = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            key_byte = xOrKeY[i % len(xOrKeY)]
            decrypted_bytes.append(byte ^ key_byte)
        return decrypted_bytes.decode('utf-8', errors='ignore')
    except Exception:
        return b64_str

def fEtChAcCoUnTiNfO(aCcEsStOkEn):
    uRl = f"https://ff-jwt-gen-api.lovable.app/api/public/token?access_token={aCcEsStOkEn}"
    rEsP = requests.get(uRl, timeout=10, verify=False)
    if rEsP.status_code != 200:
        raise Exception(f"API returned {rEsP.status_code}")
    dAtA = rEsP.json()
    if not dAtA.get('success', False):
        raise Exception("API indicated failure")
    aCcOuNtUiD = dAtA.get('account_uid', 'N/A')
    rEgIoN = dAtA.get('region', 'N/A')
    pLaTfOrMuSeD = dAtA.get('platform_type_used')
    pAyLoAd = dAtA.get('jwt_decoded', {}).get('payload', {})
    nIcKnAmEeNc = pAyLoAd.get('nickname', '')
    nIcKnAmE = dEcOdEfFnAmE(nIcKnAmEeNc) if nIcKnAmEeNc else 'Unknown'
    return aCcOuNtUiD, rEgIoN, nIcKnAmE, pLaTfOrMuSeD

def gEnErAtEmAjOrLoGiNrEsP(aCcEsStOkEn, oPeNiD, bAsEfIeLdS, pReFeRrEdPlAtFoRm=None):
    aLlPlAtFoRmS = list(range(1, 10))
    if pReFeRrEdPlAtFoRm is not None and pReFeRrEdPlAtFoRm in aLlPlAtFoRmS:
        pLaTfOrMs = [pReFeRrEdPlAtFoRm] + [p for p in aLlPlAtFoRmS if p != pReFeRrEdPlAtFoRm]
    else:
        pLaTfOrMs = aLlPlAtFoRmS

    for pLaTfOrM in pLaTfOrMs:
        try:
            gAmE = gAmEdAtA()
            for fIeLdNuMsTr, vAlUe in bAsEfIeLdS.items():
                fIeLdNuM = int(fIeLdNuMsTr)
                fIeLd = gAmEdAtA.DESCRIPTOR.fields_by_number.get(fIeLdNuM)
                if fIeLd is None:
                    continue
                if fIeLd.type == fIeLd.TYPE_STRING:
                    if isinstance(vAlUe, bytes):
                        try:
                            vAlUe = vAlUe.decode('utf-8')
                        except UnicodeDecodeError:
                            vAlUe = vAlUe.hex()
                    setattr(gAmE, fIeLd.name, str(vAlUe))
                elif fIeLd.type in (fIeLd.TYPE_INT32, fIeLd.TYPE_INT64,
                                    fIeLd.TYPE_UINT32, fIeLd.TYPE_UINT64,
                                    fIeLd.TYPE_SINT32, fIeLd.TYPE_SINT64):
                    setattr(gAmE, fIeLd.name, int(vAlUe))
                elif fIeLd.type == fIeLd.TYPE_BOOL:
                    setattr(gAmE, fIeLd.name, bool(vAlUe))
                elif fIeLd.type == fIeLd.TYPE_BYTES:
                    if isinstance(vAlUe, str):
                        try:
                            vAlUe = binascii.unhexlify(vAlUe)
                        except:
                            vAlUe = vAlUe.encode()
                    setattr(gAmE, fIeLd.name, vAlUe)
                else:
                    setattr(gAmE, fIeLd.name, vAlUe)
            gAmE.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            gAmE.open_id = oPeNiD
            gAmE.access_token = aCcEsStOkEn
            gAmE.platform_type = pLaTfOrM
            gAmE.field_99 = str(pLaTfOrM)
            gAmE.field_100 = str(pLaTfOrM)
            sEr = gAmE.SerializeToString()
            eNc = eNcRyPtDaTa(sEr)
            hEaDeRs = {
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
                "Content-Type": "application/octet-stream",
                "X-Unity-Version": "2018.4.11f1",
                "X-GA": "v1 1",
                "ReleaseVersion": "OB54"
            }
            rEsP = requests.post(mAjOrLoGiNuRl, data=eNc, headers=hEaDeRs, verify=False, timeout=10)
            if rEsP.status_code != 200:
                continue
            return rEsP.content
        except Exception:
            pass
        time.sleep(0.1)
    raise Exception("No valid response after trying all platforms 1-9")

# ---------- TELEGRAM HELPERS (using TABLE_NAME) ----------
def send_telegram_message(chat_id: int, text: str, parse_mode: str = "HTML", reply_markup: dict = None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=5)
    except:
        pass

def answer_callback_query(callback_id: str, text: str = None, show_alert: bool = False):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id}
    if text:
        payload["text"] = text
        payload["show_alert"] = show_alert
    try:
        requests.post(url, json=payload, timeout=3)
    except:
        pass

def get_user_data(chat_id: int):
    result = supabase.table(TABLE_NAME).select("*").eq("chat_id", chat_id).execute()
    return result.data[0] if result.data else None

def save_user_data(chat_id: int, data: dict):
    data["chat_id"] = chat_id
    supabase.table(TABLE_NAME).upsert(data).execute()

def main_menu_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "🎮 Login Game", "callback_data": "login"}],
            [{"text": "📊 Status", "callback_data": "status"}],
            [{"text": "⏹ Stop Session", "callback_data": "stop"}],
            [{"text": "ℹ️ About", "callback_data": "about"}],
            [{"text": "❓ Help", "callback_data": "help"}],
        ]
    }

def send_main_menu(chat_id: int, text: str = None):
    if text is None:
        text = "🎯 Welcome to Free Fire Login Engine!\nChoose an option:"
    send_telegram_message(chat_id, text, reply_markup=main_menu_keyboard())

def process_callback(chat_id: int, callback_id: str, data: str):
    user = get_user_data(chat_id)
    if data == "login":
        answer_callback_query(callback_id, "Please send your Access Token now.")
        supabase.table(TABLE_NAME).upsert({"chat_id": chat_id, "state": "awaiting_token"}).execute()
        send_telegram_message(chat_id, "🔑 Please send your Access Token as a text message.\nType /cancel to abort.")
        return
    elif data == "status":
        answer_callback_query(callback_id)
        if not user or user.get('status') != 'active':
            send_telegram_message(chat_id, "ℹ️ No active session. Use 'Login Game' to create one.", reply_markup=main_menu_keyboard())
            return
        created = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00')) if user.get('created_at') else None
        if created:
            delta = datetime.now().astimezone() - created
            duration = f"{delta.seconds//3600}h {(delta.seconds//60)%60}m {delta.seconds%60}s"
        else:
            duration = "N/A"
        sessions_count = user.get('sessions_count', 0)
        total_users_res = supabase.table(TABLE_NAME).select("chat_id", count="exact").execute()
        total_users = total_users_res.count if total_users_res.count else 0
        msg = (
            f"📊 <b>Session Status</b>\n"
            f"Status: 🟢 Active\n"
            f"━━━━━━━━━━━━━━━\n"
            f"Start: {user.get('created_at', 'N/A')}\n"
            f"Duration: {duration}\n"
            f"Open ID: <code>{user.get('open_id', 'N/A')[:20]}...</code>\n"
            f"Token: <code>{user.get('access_token', '')[:15]}...</code>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"Your stats\n"
            f" Sessions: {sessions_count}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"Total bot users\n"
            f" Users: {total_users}"
        )
        send_telegram_message(chat_id, msg, reply_markup=main_menu_keyboard())
        return
    elif data == "stop":
        answer_callback_query(callback_id)
        if not user or user.get('status') != 'active':
            send_telegram_message(chat_id, "❌ No active session to stop.", reply_markup=main_menu_keyboard())
            return
        supabase.table(TABLE_NAME).update({"status": "inactive"}).eq("chat_id", chat_id).execute()
        send_telegram_message(chat_id, "✅ Session stopped successfully!\n\nYour active session has been terminated.\nYou can now create a new session by pressing 'Login Game'.", reply_markup=main_menu_keyboard())
        return
    elif data == "about":
        answer_callback_query(callback_id)
        about_text = (
            "🤖 <b>About this bot</b>\n\n"
            "⚡ Purpose: Simplifies the login and session setup process.\n"
            "🔐 Authentication: Uses your access token to create a secure session.\n"
            "🌐 Proxy: Automatically generates a proxy URL for configuration.\n"
            "📂 Configuration: Provides localconfig.json setup instructions.\n"
            "📱 Platform support: Supports multiple login platforms.\n"
            "🚀 Interface: Fast, simple, and user-friendly.\n"
            "🔒 Privacy: Keep your access token and proxy URL private.\n"
            "📖 Note: Use this bot only with accounts you are authorized to access.\n\n"
            "Official Channel: @FREEFlRECODE\n"
            "Developer: @FounderOfKrishna"
        )
        send_telegram_message(chat_id, about_text, reply_markup=main_menu_keyboard())
        return
    elif data == "help":
        answer_callback_query(callback_id)
        help_text = (
            "📌 <b>How to use</b>\n"
            "• Click on 'Login Game'\n"
            "• Enter your access token\n"
            "• Your proxy URL will be generated automatically\n"
            "• Follow the instructions to set up localconfig.json\n"
            "• Choose any platform and login to Free Fire or Free Fire MAX\n"
            "• Once logged in, you can play unlimited matches\n\n"
            "⚠️ Do not share your access token or proxy URL with anyone.\n"
            "Keep it private.\n\n"
            "📜 Disclaimer: This bot is provided for educational and testing purposes only."
        )
        send_telegram_message(chat_id, help_text, reply_markup=main_menu_keyboard())
        return
    elif data == "cancel":
        answer_callback_query(callback_id, "Cancelled.")
        supabase.table(TABLE_NAME).update({"state": None}).eq("chat_id", chat_id).execute()
        send_main_menu(chat_id, "Action cancelled.")
        return
    else:
        answer_callback_query(callback_id, "Unknown action.")
        send_main_menu(chat_id)

def process_text_message(chat_id: int, text: str):
    user = get_user_data(chat_id)
    state = user.get('state') if user else None
    if text.lower() == '/cancel':
        if state:
            supabase.table(TABLE_NAME).update({"state": None}).eq("chat_id", chat_id).execute()
        send_main_menu(chat_id, "Cancelled.")
        return
    if state == "awaiting_token":
        aCcEsStOkEn = text.strip()
        if not aCcEsStOkEn:
            send_telegram_message(chat_id, "❌ Token cannot be empty. Please send a valid token or type /cancel.")
            return
        try:
            send_telegram_message(chat_id, "🔄 Fetching account info...")
            aCcOuNtUiD, rEgIoN, nIcKnAmE, pLaTfOrMuSeD = fEtChAcCoUnTiNfO(aCcEsStOkEn)
            send_telegram_message(chat_id, f"✅ Account: <b>{nIcKnAmE}</b> ({rEgIoN})")
            send_telegram_message(chat_id, "🔄 Inspecting token for open_id...")
            oPeNiD = iNsPeCtToKeN(aCcEsStOkEn)
            send_telegram_message(chat_id, f"✅ OpenID: <code>{oPeNiD}</code>")
            # Generate session ID
            session_id = aCcOuNtUiD if aCcOuNtUiD != 'N/A' else str(uuid.uuid4()).replace('-', '')
            existing = supabase.table(TABLE_NAME).select("session_id").eq("session_id", session_id).execute()
            if existing.data:
                session_id = str(uuid.uuid4()).replace('-', '')
            server_url = f"{WEBHOOK_BASE}/{session_id}/"
            # Store session data
            data = {
                "access_token": aCcEsStOkEn,
                "open_id": oPeNiD,
                "nickname": nIcKnAmE,
                "region": rEgIoN,
                "account_uid": aCcOuNtUiD,
                "platform_type": pLaTfOrMuSeD,
                "session_id": session_id,
                "status": "active",
                "last_login": datetime.now().isoformat(),
                "state": None,
                "sessions_count": (user.get('sessions_count', 0) + 1) if user else 1,
            }
            save_user_data(chat_id, data)

            # ----- SEND JSON FILE -----
            json_content = json.dumps({"serverUrl": server_url}, indent=2)
            telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
            payload = {
                'chat_id': chat_id,
                'caption': (
                    f"✅ <b>Session created successfully!</b>\n\n"
                    f"Server URL: <code>{server_url}</code>\n\n"
                    f"📋 <b>How to use</b>\n\n"
                    f"1️⃣ Download the <b>localconfig.json</b> file below.\n"
                    f"2️⃣ Move it to:\n"
                    f"<code>/storage/emulated/0/Android/data/com.dts.freefiremax/files/</code>\n"
                    f"   (or for Free Fire: <code>.../com.dts.freefire/</code>)\n"
                    f"3️⃣ Open Free Fire or Free Fire MAX and login with any platform.\n"
                    f"4️⃣ Enjoy unlimited matches!\n\n"
                    f"⚠️ Keep your server URL private.\n"
                    f"DM @FounderOfKrishna if you face issues."
                ),
                'parse_mode': 'HTML'
            }
            files = {
                'document': ('localconfig.json', json_content, 'application/json')
            }
            try:
                resp = requests.post(telegram_url, data=payload, files=files, timeout=10)
                if resp.status_code != 200:
                    send_telegram_message(chat_id, 
                        f"✅ Success! Server URL: {server_url}\n\nPlease create localconfig.json manually with:\n<code>{json_content}</code>",
                        reply_markup=main_menu_keyboard())
            except Exception as e:
                send_telegram_message(chat_id, 
                    f"Could not send file: {str(e)}\nServer URL: {server_url}\n\nPlease create localconfig.json manually.",
                    reply_markup=main_menu_keyboard())
            send_telegram_message(chat_id, "🔙 Return to main menu:", reply_markup=main_menu_keyboard())
        except Exception as e:
            send_telegram_message(chat_id, f"❌ Error: {str(e)}", reply_markup=main_menu_keyboard())
            supabase.table(TABLE_NAME).update({"state": None}).eq("chat_id", chat_id).execute()
        return
    else:
        send_main_menu(chat_id)

# ---------- FLASK APP ----------
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update = request.get_json()
        if not update:
            return "OK", 200
        if "callback_query" in update:
            cb = update["callback_query"]
            chat_id = cb.get("message", {}).get("chat", {}).get("id")
            callback_id = cb.get("id")
            data = cb.get("data")
            if chat_id and callback_id and data:
                process_callback(chat_id, callback_id, data)
            return "OK", 200
        if "message" in update:
            msg = update["message"]
            chat_id = msg.get("chat", {}).get("id")
            text = msg.get("text", "")
            if chat_id:
                process_text_message(chat_id, text)
            return "OK", 200
        return "OK", 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return "OK", 200

@app.route("/<session_id>/Ping", methods=["GET"])
def ping(session_id):
    return "", 200

@app.route("/<session_id>/MajorLogin", methods=["POST"])
def majorlogin(session_id):
    result = supabase.table(TABLE_NAME).select("*").eq("session_id", session_id).execute()
    if not result.data:
        return Response("Session not found", status=404)
    user = result.data[0]
    if user.get('status') != 'active':
        return Response("Session inactive", status=403)

    body = request.get_data()
    try:
        dEcRyPtEd = dEcRyPtDaTa(body)
        bAsEfIeLdS = pRoToBuFdEcOdE(dEcRyPtEd)
    except Exception as e:
        print(f"Decrypt/parse error: {e}")
        return Response("Bad request", status=400)

    try:
        aCcEsStOkEn = user['access_token']
        oPeNiD = user['open_id']
        pReFeRrEdPlAtFoRm = user.get('platform_type')
        custom_url = user.get('custom_major_login_url')
        if custom_url:
            global mAjOrLoGiNuRl
            original_url = mAjOrLoGiNuRl
            mAjOrLoGiNuRl = custom_url
            try:
                rEsPoNsE = gEnErAtEmAjOrLoGiNrEsP(aCcEsStOkEn, oPeNiD, bAsEfIeLdS, pReFeRrEdPlAtFoRm)
            finally:
                mAjOrLoGiNuRl = original_url
        else:
            rEsPoNsE = gEnErAtEmAjOrLoGiNrEsP(aCcEsStOkEn, oPeNiD, bAsEfIeLdS, pReFeRrEdPlAtFoRm)
        supabase.table(TABLE_NAME).update({"last_login": datetime.now().isoformat()}).eq("chat_id", user['chat_id']).execute()
        return Response(rEsPoNsE, content_type='application/octet-stream')
    except Exception as e:
        print(f"MajorLogin error: {e}")
        return Response("Internal server error", status=500)

@app.route("/", methods=["GET"])
def index():
    return "Bot is running.", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)