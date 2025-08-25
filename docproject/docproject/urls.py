from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from documents.views import DocumentViewSet, home, document_list, document_upload, document_detail, search, register

# Create router for API
router = DefaultRouter()
router.register(r'documents', DocumentViewSet)

urlpatterns = [
    # Template URLs
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('documents/', document_list, name='document_list'),
    path('documents/upload/', document_upload, name='document_upload'),
    path('documents/<int:pk>/', document_detail, name='document_detail'),
    path('search/', search, name='search'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='documents/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Admin URL
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/', include(router.urls)),
]