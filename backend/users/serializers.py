import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers

from foodgram.constants import MAX_EMAIL_LENGTH, MAX_NAME_LENGTH
from recipes.models import Recipe, Subscription

from .validators import username_validator

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """
    Класс для сериализации изображений в формате base64.
    """

    def to_internal_value(self, data):
        """
        Метод для преобразования изображения в формате base64
        в изображение для записи в базу.
        """

        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserCreateSerializer(BaseUserCreateSerializer):
    """
    Сериализатор для создания пользователя.
    """

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

    def validate(self, attrs):
        """
        Валидация полей username и email.
        """

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


class UserSerializer(BaseUserSerializer):
    """
    Сериализатор для работы с пользователями.
    """

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
            'avatar',
        )

    def get_is_subscribed(self, obj):
        """
        Метод для получаения информации о подписке пользователя на автора.
        """

        request = self.context.get('request')
        if request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, author=obj
            ).exists()
        return False


class AvatarUpdateDeleteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления и удаления аватара пользователя.
    """

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ['avatar', ]

    def validate(self, value):
        """
        Валидация поля аватара.
        """

        if not value.get('avatar'):
            field_name = 'avatar'
            raise serializers.ValidationError(
                {field_name: ["Обязательное поле."]}
            )
        return value


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """
    Сериализатор для уменьшенного набора рецепта.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializers(serializers.ModelSerializer):
    """
    Сериализатор для подписок.
    """

    email = serializers.EmailField(source='author.email', read_only=True)
    id = serializers.IntegerField(source='author.id', read_only=True)
    username = serializers.CharField(source='author.username', read_only=True)
    first_name = serializers.CharField(
        source='author.first_name', read_only=True
    )
    last_name = serializers.CharField(
        source='author.last_name', read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.ImageField(source='author.avatar', read_only=True)

    class Meta:
        model = Subscription
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
            'recipes',
            'recipes_count'
        )

    def validate(self, data):
        """
        Валидация данных подписки.
        """

        user = self.context['user']
        author = self.context['author']

        if 'POST' in self.context['request'].method:
            if Subscription.objects.filter(user=user, author=author).exists():
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого автора.'
                )
            if user.id == author.id:
                raise serializers.ValidationError(
                    'Вы не можете подписаться на самого себя.'
                )

        return data

    def create(self, validated_data):
        """
        Создание подписки.
        """

        user = self.context['user']
        author = self.context['author']
        favorite = Subscription.objects.create(user=user, author=author)
        return favorite

    def delete(self):
        """
        Удаление подписки.
        """

        user = self.context['user']
        author = self.context['author']
        Subscription.objects.filter(user=user, author=author).delete()

    def get_is_subscribed(self, obj):
        """
        Метод для получения информации о подписке.
        """

        request = self.context.get('request')
        return Subscription.objects.filter(
            user=request.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        """
        Метод для получения уменьшенного набора рецепта.
        """

        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeMinifiedSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        """
        Метод для получение количества рецептов автора.
        """

        return Recipe.objects.filter(author=obj.author).count()
