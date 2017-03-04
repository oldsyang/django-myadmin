from django import template
from types import FunctionType

register = template.Library()


# -###########################生成数据列表-###########################
def yield_header(changelist):
    if changelist.list_display == "__str__":  # 如果没有扩展，则列名显示为空
        yield changelist.pma.model_name
    else:
        for cl in changelist.list_display:
            if isinstance(cl, FunctionType):
                yield cl(changelist.pma, obj=None, return_header=True)
            else:
                yield changelist.pma.model_class._meta.get_field(cl).verbose_name


from django.urls import reverse


def get_change_url(changelist, pk):
    name = "%s:%s_%s_change" % (changelist.site.namespace, changelist.pma.app_label, changelist.pma.model_name)
    res_url = reverse(name, args=(pk,))
    return "{0}?{1}".format(res_url,
                            changelist.pma.get_url_params(changelist.request))


def yield_body(changelist):
    for d in changelist.result_list:
        if changelist.list_display == "__str__":  # 如果没有扩展，则触发对象的str方法
            tr = [str(d), ]
            if changelist.is_edit:
                tr.insert(0, get_change_url(changelist, d.pk))
            yield tr
        else:
            # 判断类型，如果是函数，取函数的返回值
            tr = [clo(changelist.pma, d) if isinstance(clo, FunctionType) else getattr(d, clo) for clo in
                  changelist.list_display]
            if changelist.is_edit:
                tr.insert(0, get_change_url(changelist, d.pk))
            yield tr


@register.inclusion_tag("plus/change_list_data.html")
def show_list_data(changelist):
    '''
    展示表格数据
    :param changelist: 
    :return: 
    '''

    # 这个地方的return的数据是传给了tab.html
    return {
        'body': yield_body(changelist),
        'header': yield_header(changelist),
        'changelist': changelist
    }


@register.inclusion_tag('plus/change_list_action.html')
def show_action(actions):
    return {'actions': ((item.__name__, item.title) for item in actions)}
