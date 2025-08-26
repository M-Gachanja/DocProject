from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter

# Import from views.py (not api_views)
from documents.views import home, document_list, document_upload, document_detail, search, register, login_view, DocumentViewSet

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
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Admin URL
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/', include(router.urls)),
]