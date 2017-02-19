print("################ceshi#########################")

from plus.res import site
from plus_app import models
from plus.res import PlusModelAdmin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.forms import ModelForm


class UserInfoModelForm(ModelForm):
    class Meta:
        model = models.UserInfo
        fields = "__all__"
        # 排除那些字段
        # exclude
        error_messages = {
            "name": {"required": "姓名不能为空"},
            "email": {"required": "邮箱不能为空"}
        }


class UserinfoPlusModelAdmin(PlusModelAdmin):
    model_form = UserInfoModelForm

    # obj代表的是行数据的对象
    def edit(self, obj, return_header=False):
        # obj.pk代表的是主键，在修改的时候要知道修改的对象

        # 返回列名
        if return_header: return mark_safe("操作")

        from plus.res import site
        # 通过对象找类
        # model_name = type(obj)._meta.model_name

        # 反向解析的名字
        name = "%s:%s_%s_change" % (site.namespace, self.app_label, self.model_name)

        res_url = reverse(name, args=(obj.pk,))
        res_url = "{0}?{1}".format(res_url, self.get_url_params(self.request))

        return mark_safe("<a href='%s'>编辑</a>" % res_url)

    def select(self, obj, return_header=False):

        if return_header: return "选项"

        return mark_safe("<input name='pk' value={0} type='checkbox'/>".format(obj.pk))

    def delete(self, obj, return_header=False):

        # 返回列名
        if return_header: return "删除"

        from plus.res import site

        # 反向解析的名字
        name = "%s:%s_%s_delete" % (site.namespace, self.app_label, self.model_name)

        res_url = reverse(name, args=(obj.pk,))
        res_url = "{0}?{1}".format(res_url, self.get_url_params(self.request))

        return mark_safe("<a href='%s'>删除</a>" % res_url)

    list_display = [select, "id", "name", "email", edit, delete]

    def action_delete(self, request):
        pass

    def action_update(self, request):
        pk_list = request.POST.getlist("pk")
        print("pk_list:", pk_list)
        self.model_class.objects.filter(pk__in=pk_list).update(name='yangzai')

    # action_delete也是一个对象，可以自定义属性
    action_delete.title = "批量删除"
    action_update.title = "批量更新"

    action_list = [action_delete, action_update]

    # -------组合搜索-----------

    from plus.utils.filters import FilterOption
    filter_list = [
        FilterOption("name"),
        FilterOption("ug", True),
        FilterOption("m2m"),
        FilterOption("email",text_func_name="show_email"),
    ]


class UserGroupPlusModelAdmin(PlusModelAdmin):
    list_display = ["id", "name"]


class RolePlusModelAdmin(PlusModelAdmin):
    list_display = ["id", "name"]


site.register(models.UserInfo, UserinfoPlusModelAdmin)
site.register(models.UserGroup)
site.register(models.Grade)
site.register(models.Role)
