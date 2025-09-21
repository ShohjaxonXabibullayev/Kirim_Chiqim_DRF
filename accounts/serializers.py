from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (

            "email",
            "username",
            "phone",
            "first_name",
            "last_name",

        )



class UserCreateSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "username", "phone", "first_name", "last_name", "password1", "password2")
        read_only_fields = ("id",)

    def validate(self, attrs):
        p1 = attrs.get("password1")
        p2 = attrs.get("password2")
        if p1 != p2:
            raise serializers.ValidationError({"password2": "Parollar mos kelmadi."})
        try:
            validate_password(p1)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password1": list(e.messages)})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password1")
        validated_data.pop("password2", None)
        user = User.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if not username or not password:
            raise serializers.ValidationError("Iltimos, username va password kiriting.")

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Noto‘g‘ri login yoki parol.")
        if not user.is_active:
            raise serializers.ValidationError("Foydalanuvchi faol emas.")

        attrs["user"] = user
        return attrs


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "phone", "first_name", "last_name")

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context.get("request").user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate_new_password(self, value):
        user = self.context.get("request").user
        try:
            validate_password(value, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def save(self, **kwargs):
        user = self.context.get("request").user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyResetCodeSerializer(serializers.Serializer):
    code = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        p = attrs.get("password")
        cp = attrs.get("confirm_password")
        if p != cp:
            raise serializers.ValidationError({"confirm_password": "Parollar bir xil bo‘lishi kerak."})
        try:
            validate_password(p)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return attrs

    def save(self, **kwargs):
        request = self.context.get("request")
        user = self.context.get("user")
        if not user and request:
            user_id = request.session.get("reset_user_id")
            if user_id:
                user = User.objects.filter(id=user_id).first()

        if not user:
            raise serializers.ValidationError("Foydalanuvchi aniqlanmadi — reset bajarib bo‘lmaydi.")

        user.set_password(self.validated_data["password"])
        user.save()
        return user
