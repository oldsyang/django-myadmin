from django import template
from types import FunctionType

register = template.Library()


def yield_header(data_list, list_diaplay, model_class_obj):
    if list_diaplay == "__all__":  # 如果没有扩展，则列名显示为空
        yield ""
    else:
        for cl in list_diaplay:
            if isinstance(cl, FunctionType):
                yield cl(model_class_obj, obj=None, return_header=True)
            else:
                yield model_class_obj.model_class._meta.get_field(cl).verbose_name


def yield_body(data_list, list_diaplay, model_class_obj):
    for d in data_list:
        if list_diaplay == "__all__":  # 如果没有扩展，则触发对象的str方法
            yield [str(d), ]
        else:
            # 判断类型，如果是函数，取函数的返回值
            yield [clo(model_class_obj, d) if isinstance(clo, FunctionType) else getattr(d, clo) for clo in
                   list_diaplay]


@register.inclusion_tag("tab.html")
def func_data(data_list, list_diaplay, model_class_obj):
    body = yield_body(data_list, list_diaplay, model_class_obj)
    header = yield_header(data_list, list_diaplay, model_class_obj)

    print("header:", header)

    # 这个地方的return的数据是传给了tab.html
    return {"body": body, "header": header}
