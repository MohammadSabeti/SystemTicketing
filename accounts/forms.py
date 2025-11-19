from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class RegistrationForm(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = ["first_name", "last_name","username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'user'  # مثلاً همه کاربران جدید، نقش 'user' داشته باشن
        user.profile_image = 'profile_pics/default_user_image.png'
        if commit:
            user.save()
        return user