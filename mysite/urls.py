"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path  # include - для подключения других URL-конфигураций
from django.contrib.auth import views as auth_views
from polls import views as polls_views
from django.views.generic import RedirectView

urlpatterns = [
    # Главная страница - переадресация на опросы
    path('', RedirectView.as_view(pattern_name='polls:index'), name='home'),
    
    # Все адреса, начинающиеся с polls/, передаем в polls.urls
    path("polls/", include("polls.urls")),
    
    # Админка доступна по адресу admin/
    path("admin/", admin.site.urls),

    # Аутентификация
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    
    # Выход - только через POST
    path('accounts/logout/', auth_views.LogoutView.as_view(
        template_name='registration/logged_out.html'
    ), name='logout'),
    
    # Регистрация
    path('accounts/register/', polls_views.register, name='register'),

    # Новые URL для OAuth
    path('auth/', include('social_django.urls', namespace='social')),

    path('analytics/', include('analytics.urls')),
]