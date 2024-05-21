from django.contrib import admin

from recipes.models import (Recipe, Tag, Ingredient,
                            UserFavourite, UserShoppingCart)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'author',
                    'userfavorites_count')
    search_fields = ('name',
                     'author')
    list_filter = ('tags',)
    filter_horizontal = ('ingredients', 'tags')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'measurement_unit')
    search_fields = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(UserFavourite)
admin.site.register(UserShoppingCart)
