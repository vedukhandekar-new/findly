from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User, Item, Message, Review


# ─────────────────────────────────────────
# AUTH FORMS  (your originals — fixed)
# ─────────────────────────────────────────

class UserSignupForm(UserCreationForm):
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'gender', 'mobile', 'email', 'role', 'password1', 'password2']
        widgets = {
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
            'gender':    forms.RadioSelect(),
        }


class UserLoginForm(forms.Form):
    email    = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'})
    )


class UserProfileForm(forms.ModelForm):
    # ✅ FIX: was missing model = User and was forms.Form not ModelForm
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'gender', 'mobile' , 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'gender':     forms.RadioSelect(),
            'mobile':     forms.TextInput(attrs={'class': 'form-control'}),
        }


# ─────────────────────────────────────────
# ITEM FORMS  (new)
# ─────────────────────────────────────────

class ReportLostItemForm(forms.ModelForm):
    class Meta:
        model  = Item
        fields = ['category', 'description', 'image', 'latitude', 'longitude', 'timestamp_event', 'reward_amount']
        widgets = {
            'category':        forms.Select(attrs={'class': 'form-select'}),
            'description':     forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image':           forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'latitude':        forms.HiddenInput(),
            'longitude':       forms.HiddenInput(),
            'timestamp_event': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'reward_amount':   forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
        }

    def save(self, commit=True, reporter=None):
        item = super().save(commit=False)
        item.report_type = 'Lost'
        if reporter:
            item.reporter = reporter
        if commit:
            item.save()
        return item


class ReportFoundItemForm(forms.ModelForm):
    class Meta:
        model  = Item
        fields = ['category', 'description', 'image', 'qr_code_id', 'latitude', 'longitude', 'timestamp_event']
        widgets = {
            'category':        forms.Select(attrs={'class': 'form-select'}),
            'description':     forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image':           forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'qr_code_id':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Scan or enter QR ID'}),
            'latitude':        forms.HiddenInput(),
            'longitude':       forms.HiddenInput(),
            'timestamp_event': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def save(self, commit=True, reporter=None):
        item = super().save(commit=False)
        item.report_type = 'Found'
        if reporter:
            item.reporter = reporter
        if commit:
            item.save()
        return item


class ItemSearchForm(forms.Form):
    query       = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search items...'})
    )
    category    = forms.ChoiceField(
        required=False,
        choices=[('', 'All Categories')] + Item.CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    report_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All'), ('Lost', 'Lost'), ('Found', 'Found')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    latitude    = forms.DecimalField(required=False, widget=forms.HiddenInput())
    longitude   = forms.DecimalField(required=False, widget=forms.HiddenInput())
    radius_km   = forms.IntegerField(
        required=False, initial=10,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Radius (km)'})
    )


# ─────────────────────────────────────────
# MESSAGING FORM  (new)
# ─────────────────────────────────────────

class MessageForm(forms.ModelForm):
    class Meta:
        model  = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Type your message...'})
        }


# ─────────────────────────────────────────
# REVIEW FORM  (new)
# ─────────────────────────────────────────

class ReviewForm(forms.ModelForm):
    class Meta:
        model  = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating':  forms.Select(
                choices=[(i, f'{i} ★') for i in range(1, 6)],
                attrs={'class': 'form-select'}
            ),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional feedback...'})
        }