from django.contrib import admin
from .models import Lead, ActiveOrder


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    # Делаем отображение максимально похожим на консультации
    list_display = ['name', 'status', 'created_at']
    search_fields = ['name', 'message']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Заявка', {
            'fields': ('message',)
        }),
        ('Статус', {
            'fields': ('status',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ActiveOrder)
class ActiveOrderAdmin(admin.ModelAdmin):
    """Консультации / активные заказы (канбан)"""
    list_display = ['title', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['title', 'description']
    fields = ['title', 'description', 'status']
