from django.shortcuts import render, redirect
from django.urls import reverse
from django.forms import ModelForm

from plus.utils.filters import FilterList
from plus.utils.pager import Pager
from django.db.models import ForeignKey, ManyToManyField
from django.http.request import QueryDict
from django.utils.safestring import mark_safe

import copy


class ChangeList():
    def __init__(self, pma, result_list):
        '''
        PlusModelAdmin对象
        :param pma: 
        '''
        self.pma = pma
        self.site = pma.site
        self.request = pma.request

        self.list_display = pma.list_display
        self.filter_list = pma.filter_list

        self.model_class = pma.model_class
        self.changelist_url = pma.changelist_url
        self.action_list = pma.action_list

        all_count = result_list.count()
        query_params = copy.deepcopy(self.request.GET)
        query_params._mutable = True

        self.pager = Pager(all_counts=all_count, current_page=self.request.GET.get("page"),
                           base_url=self.changelist_url,
                           params_dict=query_params)
        self.result_list = result_list[self.pager.start_index:self.pager.stop_index]

    def option_filter_list(self):
        '''
        组合搜索
        :return: 
        '''
        for option in self.filter_list:
            if option.is_func:  # 接收函数的返回值
                obj_list = option.field_or_func(self, option, self.request)
            else:
                # 获取字段（django.db.models下的字段类型）
                field = self.model_class._meta.get_field(option.field_or_func)
                if isinstance(field, ForeignKey):  # 如果是外键字段
                    # rel.model ：当前字段相关联的表
                    obj_list = FilterList(option, field.rel.model.objects.all(), self.request)
                elif isinstance(field, ManyToManyField):
                    obj_list = FilterList(option, field.rel.model.objects.all(), self.request)
                else:  # 当前model内的正常字段
                    obj_list = FilterList(option, field.model.objects.all(), self.request)

            yield obj_list

    def add_btn(self):
        """
        列表页面定制新建数据按钮
        :return: 
        """
        pass
        add_url = reverse(
            '%s:%s_%s_add' % (
                self.site.namespace, self.model_class._meta.app_label, self.model_class._meta.model_name))

        _change = QueryDict(mutable=True)
        _change['_params'] = self.request.GET.urlencode()

        tpl = "<a class='btn btn-success' style='pull-right' href='{0}?{1}'><span class='glyphicon glyphicon-share-alt' aria-hidden='true'></span> 新建数据</a>".format(
            add_url,
            _change.urlencode())
        return mark_safe(tpl)


class PlusModelAdmin(object):
    list_display = "__all__"
    action_list = []

    filter_list = []

    model_form = None

    def __init__(self, model_class, site):
        self.model_class = model_class
        self.site = site

        self.app_label = self.model_class._meta.app_label
        self.model_name = self.model_class._meta.model_name

    @property
    def urls(self):
        from django.conf.urls import url, include

        info = (self.model_class._meta.app_label, self.model_class._meta.model_name)

        # 最基本的增删改查
        urlpatterns = [
            url(r'^$', self.changelist_view, name='%s_%s_changelist' % info),
            url(r'^add/$', self.add_view, name='%s_%s_add' % info),
            url(r'^(.+)/delete/$', self.delete_view, name='%s_%s_delete' % info),
            url(r'^(.+)/change/$', self.change_view, name='%s_%s_change' % info),
        ]
        return urlpatterns

    def get_url_params(self, request):
        '''
        获取url的参数
        :param request: 
        :return: 
        '''

        # request.GET其类型就是一个QueryDict，所以有一个urlencode方法，获取所有的参数
        from django.http.request import QueryDict
        querydict = QueryDict(mutable=True)

        # 如果有参数，在添加完数据之后，需要跳转回原来的页面，所以需要保存之前的这些参数（name=yangzai&page=10）
        if request.GET:
            # 重新自定一个参数{"_params":'name=yangzai&page=10'}
            # 当跳转的时候，去除_params的值，和url拼接
            querydict["_params"] = request.GET.urlencode()  # name=yangzai&page=10
        else:
            querydict["_params"] = ""

        return querydict.urlencode()

    @property
    def changelist_param_url(self):
        '''
        获取数据列表页的url（带参数）
        :return: 
        '''
        return reverse(
            "%s:%s_%s_changelist?%s" % (
                self.site.namespace, self.app_label, self.model_name, self.request.GET.urlencode()))

    @property
    def changelist_url(self):
        '''
        获取数据列表页的url
        :return: 
        '''
        return reverse(
            "%s:%s_%s_changelist" % (
                self.site.namespace, self.app_label, self.model_name))

    def get_change_list_condition(self, query_params):
        '''
        过滤合法的查询字段
        :param query_params: 
        :return: 
        '''

        field_list = [item.name for item in self.model_class._meta._get_fields()]
        condition = {}
        for k in query_params:
            if k not in field_list:
                # raise Exception('条件查询字段%s不合法，合法字段为：%s' % (k, ",".join(field_list)))
                continue
            condition[k + "__in"] = query_params.getlist(k)
        return condition

    def changelist_view(self, request):
        '''
        显示数据列表
        :param request: 
        :return: 
        '''

        self.request = request
        result_list = self.model_class.objects.filter(**self.get_change_list_condition(request.GET))
        print("sql:", result_list.query)

        if request.method == "POST":
            action_event = request.POST.get("action")
            if not action_event:
                return redirect(self.changelist_param_url(request.GET))
            # 执行函数
            if getattr(self, action_event)(request):  # 跳转原地址
                return redirect(self.changelist_param_url(request.GET))
            else:  # 跳转到数据列表首页
                return redirect(self.changelist_url)

        change_list = ChangeList(self, result_list)

        context = {
            'chl': change_list,

        }

        # 传递的数据
        # params = {
        #     "data_list": data,
        #     "list_display": self.list_display,
        #     "modeladmin_obj": self,
        #     "add_url": add_url,
        #     "pager": pager,
        #     "action_list": action,
        #     "filter_list": filter_list
        # }
        return render(request, "plus/change_list.html", context)

    def get_model_form(self):
        '''
        生成一个默认的ModelForm
        :return: 
        '''
        if self.model_form: return self.model_form

        # ModelForm可以自动生成标签
        class MyModelForm(ModelForm):
            class Meta:
                model = self.model_class
                fields = "__all__"

        return MyModelForm

    def add_view(self, request):
        self.request = request
        if request.method == "GET":
            model_form = self.get_model_form()()
            from  django.forms.boundfield import BoundField
            return render(request, "plus/add.html", {"form": model_form, "modeladmin_obj": self})
        else:
            obj = self.get_model_form()(data=request.POST, files=request.FILES)
            _params = request.GET.get("_params")
            if obj.is_valid():
                popup_obj = obj.save()
                changelist_url = reverse(
                    "{0}:{1}_{2}_changelist".format(self.site.namespace, self.app_label, self.model_name))
                changelist_url = "%s?%s" % (changelist_url, _params)

                popup_id = request.GET.get("_popup_id")
                # 这个的话是表示这个一个新弹出的popup窗口的提交请求
                if popup_id:
                    return render(request, "plus/form_add_popup.html",
                                  {"pk": popup_obj.pk, "text": str(popup_obj), "popup_id": popup_id})
                else:
                    # 正常的请求，跳回页面
                    return redirect(changelist_url)
            else:

                return render(request, "plus/add.html", {"form": obj, "modeladmin_obj": self})

    def delete_view(self, request, pk):
        obj = self.model_class.objects.filter(pk=pk).delete()
        if not obj:
            return HttpResponse("出错了")

        _params = request.GET.get("_params")
        changelist_url = reverse(
            "{0}:{1}_{2}_changelist".format(self.site.namespace, self.app_label, self.model_name))
        changelist_url = "%s?%s" % (changelist_url, _params)

        # 跳回页面
        return redirect(changelist_url)

    def change_view(self, request, pk):
        obj = self.model_class.objects.filter(pk=pk).first()
        if not obj:
            return HttpResponse("出错了")

        if request.method == "GET":
            model_form = self.get_model_form()(instance=obj)
            return render(request, "plus/add.html", {"form": model_form, "modeladmin_obj": self})
        else:
            # 这里要加instance，才能去处理如果库里有就更新
            obj = self.get_model_form()(data=request.POST, files=request.FILES, instance=obj)
            _params = request.GET.get("_params")
            if obj.is_valid():
                obj.save()
                changelist_url = reverse(
                    "{0}:{1}_{2}_changelist".format(self.site.namespace, self.app_label, self.model_name))
                changelist_url = "%s?%s" % (changelist_url, _params)
                return redirect(changelist_url)
            else:
                return render(request, "plus/add.html", {"form": obj, "modeladmin_obj": self})


from django.shortcuts import HttpResponse


class PlusSite(object):
    def __init__(self):
        self._registry = {}
        self.namespace = "plus"
        self.app_name = "plus"

    def register(self, model_class, model_admin=PlusModelAdmin):
        self._registry[model_class] = model_admin(model_class, self)

    def login(self, request):
        return HttpResponse("login")

    def get_urls(self):
        from django.conf.urls import url, include

        ret = [
            url(r"^login/", self.login, name="login")
        ]

        for model_cls, model_am in self._registry.items():
            app_label = model_cls._meta.app_label
            model_name = model_cls._meta.model_name
            # 做路由分发include(model_am.urls)
            ret.append(url(r"^%s/%s/" % (app_label, model_name), include(model_am.urls)))
        return ret

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.namespace


# 始终只有一个site对象
site = PlusSite()
