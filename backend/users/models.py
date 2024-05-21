from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    email = models.EmailField(max_length=256,
                              verbose_name='Адрес электронной почты')
    username_validator = RegexValidator(
        regex=r'^[\w.@+-]+$',
        message='''Юзернейм должен состоять из букв, цифр
                 или содержать следующие символы: .@+-''',
    )
    username = models.CharField(max_length=150,
                                unique=True,
                                validators=[username_validator],
                                verbose_name='Юзернейм')
    name = models.CharField(max_length=150,
                            verbose_name='Имя')
    second_name = models.CharField(max_length=150,
                                   verbose_name='Фамилия')
    password = models.CharField(max_length=150,
                                verbose_name='Пароль')
    avatar = models.ImageField(upload_to='users/images',
                               verbose_name='Аватар пользователя',
                               default=None,
                               null=True)
    is_blocked = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписки',
        related_name='subscriptions'
    )
    subscription = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчики',
        related_name='subscribers'
    )

    class Meta:
        verbose_name = 'Подписчик',
        verbose_name_plural = 'Подписчики'
        unique_together = ('subscriber', 'subscription')
