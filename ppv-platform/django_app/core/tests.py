from django.test import TestCase
from django.utils import timezone
from .models import User, Content, Payment, AccessToken
from datetime import timedelta

class PaymentWebhookTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='pass')
        self.content = Content.objects.create(title='Test', description='desc', file_url='http://example.com/file', price=10)
        self.payment = Payment.objects.create(user=self.user, content=self.content, amount=10, status='pending', reference='ref123')

    def test_webhook_success(self):
        response = self.client.post('/webhooks/payment/', {'reference': 'ref123'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'successful')
        token = AccessToken.objects.filter(user=self.user, content=self.content).first()
        self.assertIsNotNone(token)
        self.assertTrue(token.is_active)
