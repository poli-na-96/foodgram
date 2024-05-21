import csv
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.serializers import (
    IngredientSerializer, RecipeCreateSerializer,
    RecipeSerializer, TagSerializer
)
from recipes.models import (
    Ingredient, Recipe, Tag, UserFavourite, UserShoppingCart
)

from rest_framework import viewsets, status


class RecipeViewSet(viewsets.ModelViewSet):
    ordering = ('-pub_date',)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        tags_slugs = self.request.GET.getlist('tags')
        is_favorited = self.request.GET.get('is_favorited')
        author_id = self.request.GET.get('author')
        queryset = Recipe.objects.all()
        if self.request.user.is_authenticated and is_favorited:
            queryset = queryset.filter(
                userfavorites__user=self.request.user
            )
        if tags_slugs:
            queryset = queryset.filter(tags__slug__in=tags_slugs)
        if author_id:
            queryset = queryset.filter(author__id=author_id)
        return queryset.distinct()

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.add_to_favorites(request, pk)
        else:
            return self.remove_from_favorites(request, pk)

    def add_to_favorites(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            UserFavourite.objects.get(user=user, recipe=recipe)
        except UserFavourite.DoesNotExist:
            UserFavourite.objects.create(user=user, recipe=recipe)
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def remove_from_favorites(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            user_fav_recipe = UserFavourite.objects.get(
                user=user, recipe=recipe
            )
        except UserFavourite.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user_fav_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.add_to_shopping_cart(request, pk)
        else:
            return self.remove_from_shopping_cart(request, pk)

    def add_to_shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            UserShoppingCart.objects.get(user=user, recipe=recipe)
        except UserShoppingCart.DoesNotExist:
            UserShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def remove_from_shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            recipe_in_shopping_card = UserShoppingCart.objects.get(
                user=user, recipe=recipe
            )
        except UserShoppingCart.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe_in_shopping_card.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        ingredient_details = {}
        recipes = UserShoppingCart.objects.filter(user=user).values_list(
            'recipe', flat=True
        )
        for recipe_id in recipes:
            recipe = Recipe.objects.get(pk=recipe_id)
            for ingredient_recipe in recipe.recipe_ingredient.all():
                ingredient = ingredient_recipe.ingredients
                amount = ingredient_recipe.amount
                unit = ingredient.measurement_unit
                if ingredient.name in ingredient_details:
                    ingredient_details[ingredient.name]['amount'] += amount
                else:
                    ingredient_details[ingredient.name] = {
                        'amount': amount,
                        'unit': unit
                    }
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = (
            'attachment; filename="ingredients_to_buy.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(['Ingredient', 'Total Amount', 'Measurement Unit'])
        for ingredient_name, details in ingredient_details.items():
            writer.writerow(
                [ingredient_name, details['amount'], details['unit']]
            )
        return response


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
