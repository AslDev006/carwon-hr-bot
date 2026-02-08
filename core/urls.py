from django.contrib import admin
from django.urls import path
from models.views import CandidateDetailView, CandidateListView, ProfileView
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.conf import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('candidate/<int:pk>/', CandidateDetailView.as_view(), name='candidate_detail'),
    path('', CandidateListView.as_view(), name='candidate_list'),
    path('profile/', ProfileView.as_view(), name='profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)