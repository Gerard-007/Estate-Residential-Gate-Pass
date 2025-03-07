from django.urls import path
from .views import GenerateTokenView, VerifyTokenView, EstateListView, EstateDetailView, ApartmentListView, \
    ApartmentDetailView

urlpatterns = [
    path('estates/', EstateListView.as_view(), name='estate_list'),
    path('estate/<int:id>/', EstateDetailView.as_view(), name='estate_detail'),
    path('apartments/', ApartmentListView.as_view(), name='apartment_list'),
    path('apartment/<int:id>/', ApartmentDetailView.as_view(), name='apartment_detail'),
    path('generate_tokens/', GenerateTokenView.as_view(), name='generate_tokens'),
    path('verify_token/<uuid:token>/', VerifyTokenView.as_view(), name='verify_token'),
]