from django.db import models
from django.forms import ModelForm
from django.forms import Form


# Create your models here.

class Role(models.Model):
    name = models.CharField(verbose_name="角色名", max_length=64)
    def __str__(self):
        return self.name


class UserGroup(models.Model):
    title = models.CharField(verbose_name="组名", max_length=64)


class UserInfo(models.Model):
    name = models.CharField(verbose_name="姓名", max_length=108)
    age = models.IntegerField(verbose_name="年龄")
    email = models.EmailField(verbose_name="邮箱")

    ug = models.ForeignKey(UserGroup)
    m2m = models.ManyToManyField(Role)

    def __str__(self):
        return self.name
