"""
URL configuration for djangofullpro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path,include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from webapp import views
from webapp.views import MyTokenObtainPairView,QuestionViewSet,DashboardViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'polls', QuestionViewSet, basename='polls')
router.register(r'dashboard',DashboardViewSet,basename='dashboard')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', MyTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),  
    path('api/', include(router.urls)),
    
    # path('csrf-token/', views.csrf_token_view, name='csrf_token'),
]
