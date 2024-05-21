import base64
import logging
from django.core.files.base import ContentFile
from rest_framework import serializers

from users.models import Subscription
from recipes.models import (
    Ingredient, IngredientRecipe, Recipe, Tag,
    TagRecipe, UserShoppingCart, UserFavourite
)

from users.serializers import MyUserSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(child=serializers.IntegerField())
    ingredients = serializers.ListField(child=serializers.DictField())
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'name', 'text', 'ingredients', 'image', 'tags', 'cooking_time'
        )

    def to_representation(self, instance):
        return RecipeSerializer().to_representation(instance)

    def create(self, validated_data):
        tags_id = validated_data.pop('tags')
        tags = Tag.objects.filter(id__in=tags_id)
        ingredients_list = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            TagRecipe.objects.create(tags=tag, recipe=recipe)
        for ingredient in ingredients_list:
            ingredient_instance = Ingredient.objects.get(
                id=ingredient['id']
            )
            IngredientRecipe.objects.create(
                ingredients=ingredient_instance,
                amount=ingredient['amount'],
                recipe=recipe
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)

        tags_id = validated_data.get('tags')
        tags = Tag.objects.filter(id__in=tags_id)

        instance.tags.clear()

        for tag in tags:
            TagRecipe.objects.create(tags=tag, recipe=instance)

        ingredients_list = validated_data.get('ingredients')
        instance.ingredients.clear()
        for ingredient_data in ingredients_list:
            ingredient_id = ingredient_data.get('id')
            amount = ingredient_data.get('amount')
            ingredient_instance = Ingredient.objects.get(id=ingredient_id)
            IngredientRecipe.objects.create(
                ingredients=ingredient_instance,
                amount=amount,
                recipe=instance
            )

        instance.save()
        return instance


class RecipeSerializer(serializers.ModelSerializer):
    author = MyUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True, source='recipe_ingredient', read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'text', 'ingredients', 'image', 'tags',
            'cooking_time', 'author', 'is_favorited', 'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserFavourite.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserShoppingCart.objects.filter(
                user=request.user, recipe=obj).exists()
        return False


class SubscriptionListSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='subscription.email')
    id = serializers.ReadOnlyField(source='subscription.id')
    username = serializers.ReadOnlyField(source='subscription.username')
    first_name = serializers.ReadOnlyField(source='subscription.first_name')
    last_name = serializers.ReadOnlyField(source='subscription.last_name')
    is_subscribed = serializers.ReadOnlyField(source='subscription.is_subscribed')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = Base64ImageField(source='subscription.avatar', required=False)

    def get_recipes(self, obj):
        user = obj.subscription
        user_recipes = user.recipes.all()
        serialized_recipes = RecipeSerializer(user_recipes, many=True)
        return serialized_recipes.data

    def get_recipes_count(self, obj):
        user_recipes_count = obj.subscriber.recipes.count()
        return user_recipes_count

    class Meta:
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'avatar', 'is_subscribed', 'recipes', 'recipes_count')
        model = Subscription


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('subscriber', 'subscription')
        model = Subscription

    def to_representation(self, instance):
        logging.info(instance)
        return SubscriptionListSerializer().to_representation(instance)