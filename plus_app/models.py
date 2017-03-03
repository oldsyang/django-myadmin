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
    def __str__(self):
        return self.title

class Grade(models.Model):
    title = models.CharField(verbose_name="班级名", max_length=64)
    def __str__(self):
        return self.title


class UserInfo(models.Model):
    name = models.CharField(verbose_name="姓名", max_length=108)
    age = models.IntegerField(verbose_name="年龄")
    email = models.EmailField(verbose_name="邮箱")

    ug = models.ForeignKey(UserGroup,verbose_name="分组")
    m2m = models.ManyToManyField(Grade,verbose_name="班级")

    def __str__(self):
        return self.name

    # 不显示__str__，而是显示email的内容
    def show_email(self):
        return self.email

    # 不匹配pk主键，而是匹配email的显示内容
    def value_email(self):
        return self.email

    # 不显示__str__，而是显示name的内容
    def show_name(self):
        return self.name

    # 不显示__str__，而是匹配email的显示内容
    def value_name(self):
        # name匹配的就是name
        return self.name
