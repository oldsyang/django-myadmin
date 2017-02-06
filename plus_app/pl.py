print("################ceshi#########################")

from plus.res import site
from plus_app import models
from plus.res import ModelClass
from django.utils.safestring import mark_safe
from django.urls import reverse


class UserinfoModelClass(ModelClass):
    # obj代表的是行数据的对象
    def edit(self, obj, return_header=False):
        print("obj:", obj)
        # obj.pk代表的是主键，在修改的时候要知道修改的对象

        # 返回列名
        if return_header: return mark_safe("<input type='checkbox'/>")

        from plus.res import site
        # 命名空间
        namespace = site.namespace
        # 获取app名和model名
        app_label = self.app_label
        model_name = self.model_name

        # 通过对象找类
        # model_name = type(obj)._meta.model_name

        # 反向解析的名字
        name = "%s:%s_%s_change" % (namespace, app_label, model_name)

        res_url = reverse(name, args=(obj.pk,))
        res_url = "{0}?{1}".format(res_url, self.get_url_params(self.request))

        return mark_safe("<a href='%s'>编辑</a>" % res_url)

    def add(self, obj, return_header=False):

        if return_header: return "评价"

        return mark_safe("<input/>")

    list_display = [add, "id", "name", "email", edit]


class UserGroupModelClass(ModelClass):
    list_display = ["id", "name"]


class RoleModelClass(ModelClass):
    list_display = ["id", "name"]


site.register(models.UserInfo, UserinfoModelClass)
site.register(models.UserGroup)
site.register(models.Grade)
site.register(models.Role)
