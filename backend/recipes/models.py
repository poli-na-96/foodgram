from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

User = get_user_model()


def validate_positive(value):
    if value < 1:
        raise ValidationError('Значение должно быть не меньше 1.')


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               related_name='recipes',
                               on_delete=models.CASCADE,
                               verbose_name='Автор публикации')
    name = models.CharField(max_length=256,
                            verbose_name='Название',
                            help_text='''Введите название блюда,
                                         не более 256 символов''')
    text = models.TextField(verbose_name='Описание',
                            help_text='''Введите описание блюда,
                                         не более 256 символов''')
    ingredients = models.ManyToManyField('Ingredient',
                                         through='IngredientRecipe',
                                         verbose_name='Ингредиенты',
                                         help_text='''Выберите ингредиенты
                                                      из списка''')
    image = models.ImageField(upload_to='recipes/images',
                              verbose_name='Картинка',
                              default=None)
    tags = models.ManyToManyField('Tag',
                                  verbose_name='Теги',
                                  through='TagRecipe')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[validate_positive],
        verbose_name='Время приготовления',
        help_text='Укажите время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        auto_now_add=True,
        help_text='Дата и время публикации.'
    )

    def __str__(self):
        return self.name

    def favourite_count(self):
        return UserFavourite.objects.filter(
            recipe=self
        ).count()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)


class Tag(models.Model):
    name = models.CharField(max_length=32,
                            unique=True,
                            verbose_name='Название',
                            help_text='Название должно быть уникальным')
    slug_validator = RegexValidator(
        regex=r'^[-a-zA-Z0-9_]+$',
        message='''Слаг должен состоять из букв, цифр
                 или содержать следующие символы: -_''',
    )
    slug = models.SlugField(max_length=32,
                            unique=True,
                            verbose_name='Слаг',
                            validators=[slug_validator],
                            help_text='Слаг должен быть уникальным')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(max_length=128,
                            verbose_name='Название',
                            help_text='''Введите название ингредиента,
                                         не более 128 символов''')
    measurement_unit = models.CharField(max_length=64,
                                        verbose_name='Единица измерения',
                                        help_text='''Введите единицу измерения,
                                            не более 64 символов''')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredients = models.ForeignKey(Ingredient,
                                    on_delete=models.CASCADE,
                                    verbose_name='Ингредиенты'
                                    )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='recipe_ingredient')
    amount = models.PositiveIntegerField(
        validators=[validate_positive],
        verbose_name='Количество',)

    class Meta:
        verbose_name = 'ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f"{self.ingredients}-{self.recipe}"


class TagRecipe(models.Model):
    tags = models.ForeignKey(Tag,
                             on_delete=models.CASCADE,
                             verbose_name='Теги')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='recipe_tag')

    class Meta:
        verbose_name = 'тег рецепта'
        verbose_name_plural = 'Теги рецептов'

    def __str__(self):
        return f"{self.tags}-{self.recipe}"


class UserFavourite(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='userfavorites')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Избранные рецепты',
                               related_name='userfavorites')

    class Meta:
        verbose_name = 'избранный рецепт пользователя'
        verbose_name_plural = 'Избранные рецепты пользователя'

    def __str__(self):
        return f"{self.user}-{self.recipe}"


class UserShoppingCart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='usershoppingcart')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Список покупок',
                               related_name='usershoppingcart')

    class Meta:
        verbose_name = 'корзина пользователя'
        verbose_name_plural = 'Продукты в корзинах подьзователей'

    def __str__(self):
        return f"{self.user}-{self.recipe}"


class Link(models.Model):
    short_link = models.CharField(max_length=128)
    long_link = models.CharField(max_length=256)

    class Meta:
        verbose_name = 'ссылка на рецепт'
        verbose_name_plural = 'Ссылки на рецепт'

    def __str__(self):
        return f"{self.short_link}-{self.long_link}"
