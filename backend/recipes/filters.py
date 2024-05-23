from django.db.models import Q
from django_filters import rest_framework as filters
from recipes.models import Ingredient


class IngredientSearchFilter(filters.FilterSet):
    name = filters.CharFilter(method='filter_name')

    class Meta:
        model = Ingredient
        fields = ['name']

    def filter_name(self, queryset, name, value):
        return queryset.filter(
            Q(name__istartswith=value)
        )
