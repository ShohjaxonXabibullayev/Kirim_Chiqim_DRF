from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    LoginSerializer,
    ProfileUpdateSerializer,
    PasswordChangeSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    VerifyResetCodeSerializer
)
import random

User = get_user_model()

class SignupView(APIView):
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Ro‘yxatdan o‘tish muvaffaqiyatli!",
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Tizimga muvaffaqiyatli kirdingiz!",
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                })
            return Response({"error": "Login yoki parol noto‘g‘ri"}, status=400)
        return Response(serializer.errors, status=400)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Tizimdan chiqdingiz"}, status=200)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profil yangilandi!", "user": serializer.data})
        return Response(serializer.errors, status=400)


    def patch(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profil yangilandi!", "user": serializer.data})
        return Response(serializer.errors, status=400)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            update_session_auth_hash(request, user)
            return Response({"message": "Parol muvaffaqiyatli o‘zgartirildi!"})
        return Response(serializer.errors, status=400)


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                code = str(random.randint(1000, 9999))
                request.session['reset_user_id'] = user.id
                request.session['reset_code'] = code
                print(f"Parolni tiklash kodi: {code}")
                return Response({"message": "Kod yuborildi (terminalda ko‘ring)."})
            return Response({"error": "Email topilmadi"}, status=404)
        return Response(serializer.errors, status=400)


class VerifyResetCodeView(APIView):
    def post(self, request):
        serializer = VerifyResetCodeSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            saved_code = request.session.get('reset_code')
            if code == saved_code:
                return Response({"message": "Kod to‘g‘ri! Endi yangi parol kiriting."})
            return Response({"error": "Kod noto‘g‘ri"}, status=400)
        return Response(serializer.errors, status=400)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            password = serializer.validated_data['password']
            user_id = request.session.get('reset_user_id')
            if not user_id:
                return Response({"error": "Sessiya muddati tugagan"}, status=400)

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"error": "Foydalanuvchi topilmadi"}, status=404)

            user.set_password(password)
            user.save()

            request.session.pop('reset_user_id', None)
            request.session.pop('reset_code', None)

            return Response({"message": "Parol muvaffaqiyatli yangilandi! Endi login qiling."})
        return Response(serializer.errors, status=400)
