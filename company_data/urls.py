from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import CompanyDataViewSet

router = DefaultRouter()
router.register(r'', CompanyDataViewSet, basename='company_data')
router.register(r'data_control', CompanyDataViewSet, basename='data_control')

urlpatterns = [
    path('', include(router.urls)),
]
