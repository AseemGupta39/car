from django.urls import path
from .views import CarListCreateView, CarDetailView



from django.urls import path
from .views import UserRegisterView, UserLoginView, CarListCreateView, CarDetailView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('cars/', CarListCreateView.as_view(), name='car-list-create'),
    path('cars/<int:pk>/', CarDetailView.as_view(), name='car-detail'),
]


