from types import FunctionType


class FilterOption(object):
    '''
    封装过滤的详细信息
    '''

    def __init__(self, field_or_func, is_multi=False, text_func_name=None, val_func_name=None):
        """
        :param field: 字段名称或函数
        :param is_multi: 是否支持多选
        :param text_func_name: 在Model中定义函数，显示文本名称，默认使用 str(对象)
        :param val_func_name:  在Model中定义函数，显示文本名称，默认使用 对象.pk
        """
        self.field_or_func = field_or_func
        self.is_multi = is_multi
        self.text_func_name = text_func_name
        self.val_func_name = val_func_name

    @property
    def is_func(self):
        if isinstance(self.field_or_func, FunctionType):
            return True

    @property
    def name(self):
        if self.is_func:
            return self.field_or_func.__name__
        else:
            return self.field_or_func


import copy

from django.utils.safestring import mark_safe


class FilterList():
    def __init__(self, option, querydict, request):
        self.option = option
        self.querydict = querydict
        self.params_dict = copy.deepcopy(request.GET)
        self.path_info = request.path_info

    def __iter__(self):

        # 加全部按钮，其功能是全都都包含，也就是在/ceshi/plus_app/userinfo/?page=1&ug=2&ug=6中，如果当前的数据是全部的班级
        # 那么在?page=1&ug=2中就不能出现ug相关的参数

        yield mark_safe("<div class='clearfix'></div>")

        yield mark_safe("<div style='float:left;margin:10px 0' class='clearfix' >")
        if self.option.name in self.params_dict:  # 如果之前就有，则删除
            # 剔除 {"ug":[2,6]},得到的pop_val是一个列表：[2,6]
            pop_val = self.params_dict.pop(self.option.name)
            # 组装全部的url
            url = "{0}?{1}".format(self.path_info, self.params_dict.urlencode())

            # 因为在下面的代码中还需要使用self.params_dict，所以刚才pop的数据需要再次加进去
            # 不要直接self.params_dict["ug"]=pop_val，得到的结果会是{"ug":[[2,6]]}
            self.params_dict.setlist(self.option.name, pop_val)

            yield mark_safe("<a href='{0}'>全部</a>".format(url))
        else:
            url = "{0}?{1}".format(self.path_info, self.params_dict.urlencode())
            yield mark_safe("<a class='active' href='{0}'>全部</a>".format(url))

        yield mark_safe("</div><div class='content-search' style='margin:10px 0'>")

        for obj in self.querydict:
            # 因为下面的代码还需要用到self.querydict，所以不能直接去修改
            params_dict = copy.deepcopy(self.params_dict)
            # 如果是函数，则直接在obj中去找函数并运行
            val = str(getattr(obj, self.option.val_func_name)() if self.option.val_func_name else obj.pk)
            text = getattr(obj, self.option.text_func_name)() if self.option.text_func_name else str(obj)

            active = False
            # 先取出当前字段的所有参数值
            value_list = params_dict.getlist(self.option.name)
            print("value_list:", value_list)
            if self.option.is_multi:
                # 如果当前值在里边，则说明是取消操作
                if val in value_list:
                    # 先剔除掉数据
                    value_list.remove(val)
                    active = True
                    # 再设置值
                    params_dict.setlist(self.option.name, value_list)
                else:  # 否则，说明是选中操作
                    params_dict.appendlist(self.option.name, val)


            else:
                if val in value_list:
                    active = True
                # 对于只能单选的项，只需要将字段名设置到参数字典里就可以
                params_dict[self.option.name] = val

            url = "{0}?{1}".format(self.path_info, params_dict.urlencode())
            if active:
                tpl = "<a class='active'  href='{0}'>{1}</a>".format(url, text)
            else:
                tpl = "<a href='{0}'>{1}</a>".format(url, text)

            yield mark_safe(tpl)

        yield mark_safe("</div>")
