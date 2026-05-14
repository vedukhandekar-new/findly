from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid


# ─────────────────────────────────────────
# USER MANAGER
# ─────────────────────────────────────────

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')
        return self.create_user(email, password, **extra_fields)


# ─────────────────────────────────────────
# USER MODEL  (your original — bug fixed)
# ─────────────────────────────────────────

class User(AbstractBaseUser):

    ROLE_CHOICES = (
        ('Admin',  'Admin'),
        ('User',  'User'),
        
    )
    GENDER_CHOICES = (
        ('Male',   'Male'),
        ('Female', 'Female'),
        ('Other',  'Other'),
    )

    email      = models.EmailField(unique=True)
    first_name = models.CharField(max_length=20, null=True, blank=True)
    last_name  = models.CharField(max_length=20, null=True, blank=True)
    gender     = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    # ✅ FIX: BigIntegerField does NOT accept max_length — use CharField instead
    mobile     = models.CharField(max_length=15, null=True, blank=True)
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='User')

    rating_score = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    otp_code       = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    is_active      = models.BooleanField(default=False)  # ← change True to False
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    is_admin   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    reward_amount   = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = []

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    def __str__(self):
        return self.email


# ─────────────────────────────────────────
# ITEM MODEL
# ─────────────────────────────────────────

class Item(models.Model):
    REPORT_TYPE_CHOICES = [('Lost', 'Lost'), ('Found', 'Found')]
    CATEGORY_CHOICES = [
        ('Electronics', 'Electronics'),
        ('Wallet',      'Wallet'),
        ('Keys',        'Keys'),
        ('Bag',         'Bag'),
        ('Documents',   'Documents'),
        ('Jewellery',   'Jewellery'),
        ('Clothing',    'Clothing'),
        ('Other',       'Other'),
    ]
    STATUS_CHOICES = [
        ('Active',    'Active'),
        ('Matching',  'Matching'),
        ('Recovered', 'Recovered'),
        ('Blocked',   'Blocked'),
        ('UnderReview', 'Under Review'),
    ]

    item_id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_items')
    report_type     = models.CharField(max_length=5,  choices=REPORT_TYPE_CHOICES)
    category        = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description     = models.TextField()
    image           = models.ImageField(upload_to='item_images/', blank=True, null=True)
    qr_code_id      = models.CharField(max_length=100, unique=True, blank=True, null=True)
    latitude        = models.DecimalField(max_digits=22, decimal_places=16, default=0)
    longitude       = models.DecimalField(max_digits=22, decimal_places=16, default=0)
    status          = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Active')
    timestamp_event = models.DateTimeField()
    reward_amount   = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    created_at      = models.DateTimeField(auto_now_add=True)
    # Add to Item model in core/models.py
    is_sensitive    = models.BooleanField(default=False)
    is_blocked      = models.BooleanField(default=False)
    blocked_reason  = models.CharField(max_length=255, null=True, blank=True)
    blocked_by      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='blocked_items')
    blocked_at      = models.DateTimeField(null=True, blank=True)
    flagged_by      = models.ManyToManyField(User, blank=True, related_name='flagged_items')
    flag_count      = models.IntegerField(default=0)

    def __str__(self):
        return f"[{self.report_type}] {self.category} by {self.reporter.email} — {self.status}"


# ─────────────────────────────────────────
# MATCH MODEL
# ─────────────────────────────────────────

class Match(models.Model):
    MATCH_STATUS_CHOICES = [
        ('Pending',  'Pending'),
        ('Verified', 'Verified'),
        ('False',    'False Match'),
    ]

    match_id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lost_item     = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='lost_matches')
    found_item    = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='found_matches')
    ai_confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    match_status  = models.CharField(max_length=10, choices=MATCH_STATUS_CHOICES, default='Pending')
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Match [{self.match_status}] confidence: {self.ai_confidence}%"


# ─────────────────────────────────────────
# MESSAGE MODEL
# ─────────────────────────────────────────

class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match      = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='messages')
    sender     = models.ForeignKey(User,  on_delete=models.CASCADE, related_name='sent_messages')
    content    = models.TextField()
    sent_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.email} at {self.sent_at}"


# ─────────────────────────────────────────
# NOTIFICATION MODEL
# ─────────────────────────────────────────

class Notification(models.Model):
    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message         = models.TextField()
    is_read         = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.recipient.email}: {self.message[:40]}"


# ─────────────────────────────────────────
# REVIEW MODEL
# ─────────────────────────────────────────

class Review(models.Model):
    review_id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    author      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    item        = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='reviews')
    rating      = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment     = models.CharField(max_length=255, blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.email} → {self.target_user.email}: {self.rating}★"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Auto-update target user's average rating
        from django.db.models import Avg
        avg = Review.objects.filter(target_user=self.target_user).aggregate(Avg('rating'))['rating__avg']
        if avg:
            self.target_user.rating_score = round(avg, 2)
            self.target_user.save()


# PAYMENT MODEL
# ─────────────────────────────────────────

class Payment(models.Model):
    STATUS_CHOICES = [
        ('Pending',   'Pending'),
        ('Completed', 'Completed'),
        ('Failed',    'Failed'),
    ]
    payment_id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match              = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='payment')
    payer              = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_made')
    receiver           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_received')
    amount             = models.DecimalField(max_digits=8, decimal_places=2)
    status             = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    transaction_id     = models.CharField(max_length=100, blank=True, null=True)
    created_at         = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment ₹{self.amount} from {self.payer.email} → {self.receiver.email} [{self.status}]"