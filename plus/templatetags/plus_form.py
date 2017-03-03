from django.forms import ModelChoiceField
from django.forms import ModelMultipleChoiceField
from plus.options import site
from django.urls import reverse
from django.forms import fields
from django import template
from types import FunctionType

register = template.Library()

def get_form_data(form):
    # form_list = []
    for item in form:
        # is_popup：是否增加添加按钮；popup_url：填出的url地址；data：原数据
        c_item = {"is_popup": False, "data": item, "popup_url": None}
        if isinstance(item.field, ModelChoiceField) and item.field.queryset.model in site._registry:

            c_item["is_popup"] = True

            reverse_url = "{0}:{1}_{2}_add".format(site.namespace,
                                                   item.field.queryset.model._meta.app_label,
                                                   item.field.queryset.model._meta.model_name)

            c_item["popup_url"] = reverse(reverse_url)
            # 标记这个新弹出的一个窗口：/ceshi/plus_app/uerinfo/?_popup_id=id_ug
            # item.auto_id：取select标签的id，方便在关闭新窗口之后，将值回传给哪个标签
            if "?" in c_item["popup_url"]:
                c_item["popup_url"] = "".join([c_item["popup_url"], "&", "_popup_id=", item.auto_id])
            else:
                c_item["popup_url"] = "".join([c_item["popup_url"], "?", "_popup_id=", item.auto_id])

        yield c_item


@register.inclusion_tag("plus/create_form.html")
def create_form(form, modeladmin_obj):
    s = get_form_data(form)
    return {"form": s}