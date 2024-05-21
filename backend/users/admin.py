from django.contrib import admin
from django.contrib.auth import get_user_model


User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = ('email',
                    'username',
                    'name',
                    'second_name')
    search_fields = ('email',
                     'username')


admin.site.register(User, UserAdmin)
