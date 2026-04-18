
import uuid
import json
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from .models import Payment, AccessToken, Content, User
from .payment_providers import verify_payment
from django_redis import get_redis_connection
# DRF imports for API endpoints
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

import os
from .serializers import ContentSerializer, PaymentSerializer

@csrf_exempt
def payment_webhook(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    try:
        data = json.loads(request.body)
        reference = data.get('reference')
        payment = Payment.objects.get(reference=reference)
        if payment.status != 'pending':
            return JsonResponse({'status': 'already processed'})
        # Abstracted verification
        if not verify_payment(reference):
            payment.status = 'failed'
            payment.save()
            return JsonResponse({'status': 'failed'})
        payment.status = 'successful'
        payment.save()
        # Generate access token
        expires_at = timezone.now() + timedelta(hours=24)
        token_obj = AccessToken.objects.create(
            user=payment.user,
            content=payment.content,
            expires_at=expires_at,
            max_uses=1,
            is_active=True
        )
        # Store in Redis
        redis_conn = get_redis_connection()
        token_data = {
            'token': str(token_obj.token),
            'user_id': token_obj.user_id,
            'content_id': token_obj.content_id,
            'expires_at': token_obj.expires_at.isoformat(),
            'max_uses': token_obj.max_uses,
            'used_count': token_obj.used_count,
            'is_active': token_obj.is_active,
        }
        ttl = int((token_obj.expires_at - timezone.now()).total_seconds())
        redis_conn.set(f"ppv:token:{token_obj.token}", json.dumps(token_data), ex=ttl)
        return JsonResponse({'status': 'success', 'token': str(token_obj.token)})
    except Payment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# List all available content (for frontend)
@api_view(['GET'])
@permission_classes([AllowAny])
def content_list(request):
    queryset = Content.objects.all()
    serializer = ContentSerializer(queryset, many=True)
    return Response(serializer.data)

# Create a payment (for frontend)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_payment(request):
    # Expects: {"user_id": <id>, "content_id": <id>, "amount": <amount>, "reference": <reference>}
    data = request.data
    user_id = data.get('user_id')
    content_id = data.get('content_id')
    amount = data.get('amount')
    reference = data.get('reference')
    if not (user_id and content_id and amount and reference):
        return Response({'error': 'Missing fields'}, status=400)
    try:
        user = User.objects.get(id=user_id)
        content = Content.objects.get(id=content_id)
        payment = Payment.objects.create(
            user=user,
            content=content,
            amount=amount,
            status='pending',
            reference=reference
        )
        # Initiate STK Push
        from .bank_stk import initiate_stk_push
        msisdn = data.get('msisdn')
        narration = f"Payment for {content.title} by {user.email}"
        callback_url = os.getenv('COOPBANK_CALLBACK_URL', 'http://url-to-webapp')
        if not msisdn:
            return Response({'error': 'Missing msisdn (phone number)'}, status=400)
        stk_response, status_code = initiate_stk_push(msisdn, amount, reference, narration, callback_url)
        serializer = PaymentSerializer(payment)
        return Response({
            'payment': serializer.data,
            'stk_push': stk_response,
            'stk_status_code': status_code
        }, status=201 if status_code in [200,201] else 400)
    except Exception as e:
        return Response({'error': str(e)}, status=400)
