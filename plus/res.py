from django.shortcuts import render, redirect
from django.urls import reverse
from django.forms import ModelForm


class PlusModelAdmin(object):
    list_display = "__all__"

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

    def changelist_view(self, request):

        self.request = request

        # 获取当前url的参数
        querydict = self.get_url_params(request)
        base_url = reverse(
            "%s:%s_%s_add" % (self.site.namespace, self.model_class._meta.app_label, self.model_class._meta.model_name))

        add_url = "%s?%s" % (base_url, querydict)

        # -----------------分页------------------------------
        from plus.utils.pager import Pager

        condition = {}
        # 获取数量
        all_count = self.model_class.objects.filter(**condition).count()
        current_page = request.GET.get("page")

        # 解析url地址
        base_page_url = reverse(
            "%s:%s_%s_changelist" % (
                self.site.namespace, self.model_class._meta.app_label, self.model_class._meta.model_name))

        # 解析参数


        # _mutable为True，才可以修改
        # request.GET._mutable = True

        import copy
        params_dict = copy.deepcopy(request.GET)
        # _mutable为True，才可以修改
        params_dict._mutable = True

        pager = Pager(all_counts=all_count, current_page=current_page, base_url=base_page_url,
                      params_dict=params_dict)

        data = self.model_class.objects.all()[pager.start_index:pager.stop_index]

        # 传递的数据
        params = {
            "data_list": data,
            "list_display": self.list_display,
            "modeladmin_obj": self,
            "add_url": add_url,
            "pager": pager.pager()
        }
        return render(request, "change_list.html", params)

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
            return render(request, "add.html", {"form": model_form, "modeladmin_obj": self})
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
                    return render(request, "form_add_popup.html",
                                  {"pk": popup_obj.pk, "text": str(popup_obj), "popup_id": popup_id})
                else:
                    # 正常的请求，跳回页面
                    return redirect(changelist_url)
            else:

                return render(request, "add.html", {"form": obj, "modeladmin_obj": self})

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
            return render(request, "add.html", {"form": model_form, "modeladmin_obj": self})
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
                return render(request, "add.html", {"form": obj, "modeladmin_obj": self})


from django.shortcuts import HttpResponse


class PlSite(object):
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
site = PlSite()
