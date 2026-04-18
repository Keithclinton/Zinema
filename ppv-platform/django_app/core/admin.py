from django.contrib import admin
from django.db import models
from .models import User, Content, Payment, AccessToken

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email',)
    list_filter = ('is_active', 'is_staff')

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'links_sold', 'total_revenue')
    search_fields = ('title',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # If not superuser, only show content owned by this user
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def links_sold(self, obj):
        # Number of AccessTokens for this content
        return obj.accesstoken_set.count()
    links_sold.short_description = 'Links Sold'

    def total_revenue(self, obj):
        # Sum of successful payments for this content
        return obj.payment_set.filter(status='successful').aggregate(models.Sum('amount'))['amount__sum'] or 0
    total_revenue.short_description = 'Total Revenue'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content', 'amount', 'status', 'reference', 'created_at')
    search_fields = ('user__email', 'content__title', 'reference')
    list_filter = ('status', 'created_at')

@admin.register(AccessToken)
class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'token', 'user', 'content', 'expires_at', 'max_uses', 'used_count', 'is_active')
    search_fields = ('token', 'user__email', 'content__title')
    list_filter = ('is_active', 'expires_at')
