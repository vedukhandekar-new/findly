from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Item, Match, Message, Notification, Review


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    filter_horizontal = ()  # ✅ FIX: override BaseUserAdmin's groups/user_permissions
    list_display  = ('email', 'first_name', 'last_name', 'role', 'rating_score', 'is_active')
    list_filter   = ('role', 'is_active')
    search_fields = ('first_name', 'last_name', 'email')
    ordering          = ('-created_at',)
    # ✅ FIX: clear these — our User model has no groups or user_permissions
    filter_horizontal = ()
    fieldsets     = (
        (None,            {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'gender', 'mobile', 'role', 'rating_score')}),
        ('Permissions',   {'fields': ('is_active', 'is_staff', 'is_admin')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display  = ('category', 'report_type', 'status', 'reporter', 'timestamp_event', 'created_at')
    list_filter   = ('report_type', 'category', 'status')
    search_fields = ('description', 'qr_code_id')
    ordering      = ('-created_at',)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display  = ('match_id', 'lost_item', 'found_item', 'ai_confidence', 'match_status', 'created_at')
    list_filter   = ('match_status',)
    ordering      = ('-created_at',)
    actions       = ['mark_verified', 'mark_false']

    def mark_verified(self, request, queryset):
        queryset.update(match_status='Verified')
    mark_verified.short_description = "Mark selected matches as Verified"

    def mark_false(self, request, queryset):
        queryset.update(match_status='False')
    mark_false.short_description = "Mark selected matches as False"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'match', 'sent_at')
    ordering     = ('-sent_at',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'is_read', 'created_at')
    list_filter  = ('is_read',)
    ordering     = ('-created_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'target_user', 'rating', 'item', 'created_at')
    list_filter  = ('rating',)
    ordering     = ('-created_at',)