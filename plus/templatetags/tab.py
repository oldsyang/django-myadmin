from django import template
from types import FunctionType

register = template.Library()


# -###########################生成数据列表-###########################
def yield_header(data_list, list_diaplay, modeladmin_obj):
    if list_diaplay == "__all__":  # 如果没有扩展，则列名显示为空
        yield ""
    else:
        for cl in list_diaplay:
            if isinstance(cl, FunctionType):
                yield cl(modeladmin_obj, obj=None, return_header=True)
            else:
                yield modeladmin_obj.model_class._meta.get_field(cl).verbose_name


def yield_body(data_list, list_diaplay, modeladmin_obj):
    for d in data_list:
        if list_diaplay == "__all__":  # 如果没有扩展，则触发对象的str方法
            yield [str(d), ]
        else:
            # 判断类型，如果是函数，取函数的返回值
            yield [clo(modeladmin_obj, d) if isinstance(clo, FunctionType) else getattr(d, clo) for clo in
                   list_diaplay]


@register.inclusion_tag("tab.html")
def func_data(data_list, list_diaplay, modeladmin_obj):
    body = yield_body(data_list, list_diaplay, modeladmin_obj)
    header = yield_header(data_list, list_diaplay, modeladmin_obj)

    print("header:", header)

    # 这个地方的return的数据是传给了tab.html
    return {"body": body, "header": header}


# -###########################生成数据列表结束#-###########################



# -###########################生成自定义的form之方式一###########################
# def get_form_data(form, modeladmin_obj):
#     for item in form:
#         error = ""
#         # 如果有错误并且含有当前字段的错误
#         if form.errors and form.errors.get(item.name):
#             error = form.errors.get(item.name)[0]
#
#         yield {
#             "form_tag": item,
#             "name": modeladmin_obj.model_class._meta.get_field(item.name).verbose_name,
#             "error": error
#
#         }
#
#
# @register.inclusion_tag("create_form.html")
# def create_form(form, modeladmin_obj):
#     s = get_form_data(form, modeladmin_obj)
#     return {"form": s}



# -###########################生成自定义的form之方式=二###########################

from django.forms import ModelChoiceField
from django.forms import ModelMultipleChoiceField
from plus.res import site
from django.urls import reverse


def get_form_data(form):
    # form_list = []
    for item in form:
        c_item = {"is_popup": False, "data": item, "popup_url": None}
        if isinstance(item.field, ModelChoiceField) and item.field.queryset.model in site._registry:
            c_item["is_popup"] = True

            reverse_url = "{0}:{1}_{2}_add".format(site.namespace,
                                                   item.field.queryset.model._meta.app_label,
                                                   item.field.queryset.model._meta.model_name)
            print("reverse_url:", reverse_url)
            c_item["popup_url"] = reverse(reverse_url)
            print("popup_url:", c_item["popup_url"])
        # form_list.append(c_item)
        yield c_item




@register.inclusion_tag("create_form.html")
def create_form(form, modeladmin_obj):
    s = get_form_data(form)
    return {"form": s}
