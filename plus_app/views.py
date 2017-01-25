from django.shortcuts import render, HttpResponse
from django.forms import ModelForm
from plus_app import models


# Create your views here.
class UserInfoForm(ModelForm):
    class Meta:
        model = models.UserInfo
        fields = "__all__"
        error_messages = {
            "name": {"required": "名字不能为空", "invalid": "格式不正确"},
            "age": {"required": "年龄不能为空", "invalid": "必须为数字"},
            "email": {"required": "邮箱不能为空", "invalid": "格式错误"},
        }


def test(request):
    if request.method == "GET":
        uf = UserInfoForm()
        return render(request, "test.html", {"obj": uf})
    else:
        uf = UserInfoForm(request.POST)
        if uf.is_valid():
            uf.save()
            return HttpResponse("...")
        else:
            return render(request, "test.html", {"obj": uf})

from django.urls import reverse
def test2(request):
    reverse("plus:login")
    return HttpResponse(reverse("plus:login"),request)