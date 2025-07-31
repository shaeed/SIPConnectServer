import base64
import json
import time

from google.oauth2 import service_account
from google.auth.transport.requests import Request

from app.database import get_oauth2_token, update_oauth2_token, get_service_account_file_path

# oAuth2 token valid for 60 minutes, A time after which tokens should be renewed
TIME_TO_RENEW = 50 * 60 # 50 minutes * 60 SECONDS

# Scopes required for Firebase Cloud Messaging
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]

def get_authorized_session() -> (str, int):
    credentials = service_account.Credentials.from_service_account_file(
        get_service_account_file_path(), scopes=SCOPES
    ).with_always_use_jwt_access(True)
    credentials.refresh(Request())
    jwt_decoded = decode_jwt_part(credentials.token)
    token_expiry = jwt_decoded['exp']
    print('New token generated, expiry:', token_expiry)
    return credentials.token, token_expiry

def decode_jwt_part(jwt, part='payload'):
    parts = jwt.split('.')
    b64 = parts[1 if part == 'payload' else 0] + '=='
    return json.loads(base64.urlsafe_b64decode(b64))

def get_oauth_token(username: str) -> str:
    token_dict = get_oauth2_token(username)
    if not token_dict:
        raise Exception(f'Invalid user {username}')

    expiry_time = token_dict['oauth2_token_expiry']
    current_time = int(time.time())
    if current_time > expiry_time:
        # Get new oAuth token
        token, expiry = get_authorized_session()
        update_oauth2_token(username, token, expiry)
        return token
    else:
        return token_dict['oauth2_token']
