from django.contrib import admin
from django.forms import ModelForm
from plus_app import models


# Register your models here.
# @admin.register(models.UserInfo)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ["id","name"]

class UserAdmin(admin.ModelAdmin):
    def res(self):
        return "<a>2323</a>"
    list_display = ["id", "name", res]


admin.site.register(models.UserInfo, UserAdmin)
admin.site.register(models.UserGroup)
admin.site.register(models.Role)
