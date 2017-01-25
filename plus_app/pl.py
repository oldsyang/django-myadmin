print("################ceshi#########################")

from plus.res import site
from plus_app import models
from plus.res import ModelClass
from django.utils.safestring import mark_safe


class UserinfoModelClass(ModelClass):
    # obj代表的是model对象
    def edit(obj, return_header=False):
        print("obj:", obj)
        # obj.pk代表的是主键，在修改的时候要知道修改的对象

        # 返回列名
        if return_header: return mark_safe("<input type='checkbox'/>")

        from plus.res import site
        namespace = site.namespace

        app_label = type(obj)._meta.app_label
        model_name = type(obj)._meta.model_name

        name = "%s:%s_%s_change" % (namespace, app_label, model_name)
        from django.urls import reverse

        res_url = reverse(name, args=(obj.pk,))

        return mark_safe("<a href='%s'>编辑</a>" % res_url)

    def add(obj, return_header=False):

        if return_header: return "评价"

        return mark_safe("<input/>")

    list_display = [add, "id", "name", "email", edit]


class UserGroupModelClass(ModelClass):
    list_display = ["id", "name"]


class RoleModelClass(ModelClass):
    list_display = ["id", "name"]


site.register(models.UserInfo, UserinfoModelClass)
site.register(models.UserGroup)
site.register(models.Role)
