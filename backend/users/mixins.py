from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UsernameAndEmailValidatorMixin:
    """Миксин сериализатора юзера."""

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')

        if username == 'me':
            raise serializers.ValidationError(
                'Использование имени "me" запрещено.'
            )        

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                'Этот username уже используется.'
            )

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Этот email уже используется.'
            )

        return attrs
