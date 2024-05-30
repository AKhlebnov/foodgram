import base64
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .mixins import UsernameAndEmailValidatorMixin
from .validators import username_validator
from foodgram.constants import MAX_NAME_LENGTH, MAX_EMAIL_LENGTH

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserCreateSerializer(
    UsernameAndEmailValidatorMixin,
    BaseUserCreateSerializer
):

    email = serializers.EmailField(
        required=True,
        max_length=MAX_EMAIL_LENGTH
    )
    username = serializers.CharField(
        required=True,
        max_length=MAX_NAME_LENGTH,
        validators=[
            username_validator
        ]
    )
    first_name = serializers.CharField(
        required=True,
        max_length=MAX_NAME_LENGTH,
    )
    last_name = serializers.CharField(
        required=True,
        max_length=MAX_NAME_LENGTH,
    )
    password = serializers.CharField(write_only=True, required=True)

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password'
        )


class UserSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.subscriptions.filter(author=obj).exists()
        return False


class AvatarUpdateDeleteSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ['avatar', ]

    def validate(self, value):
        if not value.get('avatar'):
            field_name = 'avatar'
            raise serializers.ValidationError(
                {field_name: ["Обязательное поле."]}
            )
        return value
