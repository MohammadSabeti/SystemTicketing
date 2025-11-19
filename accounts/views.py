from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView,LogoutView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth import login
from accounts.forms import RegistrationForm
from accounts.models import UserProfile
from django.contrib.auth import login, authenticate
from django.contrib import messages
# Create your views here.

class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tickets:ticket_list')

class UserLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


class UserRegisterView(CreateView):
    model = UserProfile
    form_class = RegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy("tickets:ticket_list")


    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get("username")
        raw_password = form.cleaned_data.get("password1")

        # ورود خودکار کاربر
        # احراز هویت کاربر (ست شدن backend)
        user = authenticate(self.request, username=username, password=raw_password)
        if user is not None:
            login(self.request, user)
            print(f"Welcome {username}! You are now logged in.")

        return response



class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    fields = ['first_name', 'last_name', 'username', 'email', 'phone_number']
    template_name = "accounts/profile.html"
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'اطلاعات پروفایل شما با موفقیت ذخیره شد.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'لطفاً خطاهای فرم را بررسی کنید.')
        return super().form_invalid(form)

class ProfileImageUploadView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    fields = ['profile_image']  # فقط فیلد تصویر
    template_name = 'accounts/profile.html'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'تصویر پروفایل شما با موفقیت آپلود شد.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'لطفاً یک تصویر معتبر انتخاب کنید (JPEG, PNG, GIF).')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('accounts:profile')


