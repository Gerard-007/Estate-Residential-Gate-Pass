from django.conf import settings
from django.core.mail import send_mail
from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from datetime import datetime, timedelta
from django.utils import timezone
from .models import User
from .serializers import RegisterSerializer, TokenSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.validated_data

        payload = {
            'user_data': {
                'email': user_data['email'],
                'phone': user_data['phone'],
                'password': user_data['password'],
                'status': user_data.get('status', 'Visitor')
            },
            'exp': datetime.now() + timedelta(hours=1)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        verification_link = f"{settings.FRONTEND_URL}/verify/{token}"
        try:
            send_mail(
                'Verify Your Email',
                f'Click this link to verify your email: {verification_link}',
                'gerardnwazk@gmail.com',
                [user_data['email']],
                fail_silently=False
            )
        except Exception as e:
            return Response({'error': 'Failed to send email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Verification email sent.'}, status=status.HTTP_201_CREATED)


class VerifyEmailView(generics.GenericAPIView):
    def get(self, request, token):
        try:
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_data = decoded['user_data']
            exp = decoded.get('exp', 0)
            if timezone.now().timestamp() > exp:
                return Response({'error': 'Token expired.'}, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(email=user_data['email']).exists():
                return Response({'error': 'Email already registered.'}, status=status.HTTP_400_BAD_REQUEST)
        except (jwt.exceptions.DecodeError, KeyError):
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            email=user_data['email'],
            phone=user_data['phone'],
            password=user_data['password'],
            status=user_data.get('status', 'Visitor')
        )

        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
        return Response(tokens, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

