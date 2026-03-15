from django.db import models
from django.conf import settings

# Create your models here.

class User(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)

    # Admin / Owner / Finder
    role = models.CharField(max_length=20)

    rating = models.IntegerField(default=5)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

class Item(models.Model):
    reporterID = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    # Lost or Found
    report_type = models.CharField(max_length=10)

    category = models.CharField(max_length=50)
    description = models.TextField()

    image = models.CharField(max_length=200, null=True, blank=True)
    qr_code = models.CharField(max_length=100, null=True, blank=True)

    latitude = models.FloatField()
    longitude = models.FloatField()

    status = models.CharField(max_length=20, default="Active")

    date_time = models.DateTimeField()

    def __str__(self):
        return self.category


class Match(models.Model):
    lost_itemID = models.ForeignKey(Item, related_name="lost", on_delete=models.CASCADE)
    found_itemID = models.ForeignKey(Item, related_name="found", on_delete=models.CASCADE)

    ai_confidence = models.FloatField()
    match_status = models.CharField(max_length=20)

    def __str__(self):
        return self.match_status


class Message(models.Model):
    matchID = models.ForeignKey(Match, on_delete=models.CASCADE)
    senderID = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content


class Review(models.Model):
    target_userID = models.ForeignKey(User, related_name="received_reviews", on_delete=models.CASCADE)
    authorID = models.ForeignKey(User, related_name="given_reviews", on_delete=models.CASCADE)

    rating = models.IntegerField()
    comment = models.CharField(max_length=255)

    itemID = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return self.comment