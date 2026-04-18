import os

PAYMENT_PROVIDER = os.getenv('PAYMENT_PROVIDER', 'stripe')

# Abstract payment verification

def verify_payment(reference):
    if PAYMENT_PROVIDER == 'stripe':
        # Integrate Stripe verification here
        return True  # Mock
    elif PAYMENT_PROVIDER == 'flutterwave':
        # Integrate Flutterwave verification here
        return True  # Mock
    return False
