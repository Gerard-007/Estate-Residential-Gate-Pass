from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from estate_visitors_gatepass.custom_permissions import IsResidentAndHasApartment, IsAdminUser, IsOwner
from .models import VisitorToken, Apartment, Estate
from .serializers import GenerateTokenSerializer, EstateSerializer, ApartmentSerializer


class EstateListView(ListCreateAPIView):
    serializer_class = EstateSerializer
    queryset = Estate.objects.all()
    permission_classes = [IsAuthenticated, IsOwner, IsAdminUser]

    def perform_create(self, serializer):
        return serializer.save(estate_manager=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(estate_manager=self.request.user)


class EstateDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = EstateSerializer
    queryset = Estate.objects.all()
    permission_classes = [IsAuthenticated, IsOwner, IsAdminUser]
    lookup_field = 'id'

    def get_queryset(self):
        return self.queryset.filter(estate_manager=self.request.user)


class ApartmentListView(ListCreateAPIView):
    serializer_class = ApartmentSerializer
    queryset = Apartment.objects.all()
    permission_classes = [IsAuthenticated, IsOwner, IsAdminUser]

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class ApartmentDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ApartmentSerializer
    queryset = Apartment.objects.all()
    permission_classes = [IsAuthenticated, IsOwner, IsAdminUser]
    lookup_field = 'id'

    def get_queryset(self):
        return self.queryset.filter(estate=self.request.user.estate_manager)


class GenerateTokenView(APIView):
    permission_classes = [IsAuthenticated, IsResidentAndHasApartment]

    def post(self, request):
        serializer = GenerateTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        expires_at = timezone.now() + timedelta(minutes=data['expiration'])

        apartment = getattr(request.user, 'apartment', None)

        if not apartment:
            return Response({
                "error": "User does not have an associated apartment."
            }, status=status.HTTP_400_BAD_REQUEST)

        visitor_token = VisitorToken.objects.create(
            visitor_name=data['visitor_name'],
            visitor_phone=data.get('visitor_phone', ''),
            visitor_email=data.get('visitor_email', ''),
            expires_at=expires_at,
            resident=request.user
        )

        return Response({
            "token": str(visitor_token.token),
            "expires_at": expires_at.isoformat()
        }, status=status.HTTP_201_CREATED)


class VerifyTokenView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, token):
        try:
            visitor_token = VisitorToken.objects.select_related('resident').get(token=token)
        except VisitorToken.DoesNotExist:
            return Response({
                "valid": False,
                "message": "Token does not exist"
            }, status=status.HTTP_404_NOT_FOUND)

        if visitor_token.expires_at < timezone.now():
            return Response({
                "valid": False,
                "message": "Token has expired"
            }, status=status.HTTP_410_GONE)

        apartment = visitor_token.resident.apartment
        estate = apartment.estate

        response = {
            "valid": True,
            "visitor_name": visitor_token.visitor_name,
            "visitor_phone": visitor_token.visitor_phone,
            "visitor_email": visitor_token.visitor_email,
            "expires_at": visitor_token.expires_at.isoformat(),
            "resident": {
                "email": visitor_token.resident.email,
                "status": visitor_token.resident.status
            },
            "apartment": {
                "name": apartment.name,
                "estate": {
                    "name": estate.name,
                    "city": estate.city,
                    "address": estate.address
                }
            }
        }
        return Response(response, status=status.HTTP_200_OK)