
import requests
import os

def get_coopbank_access_token():
    """
    Obtain OAuth2 access token from Co-op Bank.
    Uses provided access token if set, else requests a new one.
    Returns: access_token (str)
    """
    # Use provided sandbox access token if present
    sandbox_token = os.getenv('COOPBANK_ACCESS_TOKEN')
    if sandbox_token:
        return sandbox_token
    token_url = os.getenv('COOPBANK_TOKEN_URL', 'https://openapi-sandbox.co-opbank.co.ke/token')
    client_id = os.getenv('COOPBANK_CLIENT_ID', '1JRdmFBf8MPTRXrn7O7Kju4LNQoa')
    client_secret = os.getenv('COOPBANK_CLIENT_SECRET', 'WyK60jsVRCy6vgRkrafBiscEdfIa')
    data = {
        'grant_type': 'client_credentials',
        'scope': 'default',
    }
    resp = requests.post(token_url, data=data, auth=(client_id, client_secret), timeout=30)
    resp.raise_for_status()
    return resp.json()['access_token']

def initiate_stk_push(msisdn, amount, reference, narration, callback_url=None):
    """
    Initiate a Safaricom STK Push via Co-op Bank API.
    Args:
        msisdn (str): Target mobile number (e.g., 2547XXXXXXXX)
        amount (str): Amount to charge
        reference (str): Unique transaction reference
        narration (str): Transaction narration
        callback_url (str): Your webhook for payment result
    Returns:
        dict: API response
    """
    api_url = os.getenv('COOPBANK_STK_URL', 'https://openapi-sandbox.co-opbank.co.ke/stkpush/safaricom/1.0.0/')
    access_token = get_coopbank_access_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {access_token}",
    }
    data = {
        "MessageReference": reference,
        "TargetMSISDN": msisdn,
        "CallBackUrl": callback_url or os.getenv('COOPBANK_CALLBACK_URL', 'http://url-to-webapp'),
        "TransactionAmount": amount,
        "TransactionNarration": narration,
    }
    resp = requests.post(api_url, json=data, headers=headers, timeout=30)
    return resp.json(), resp.status_code
