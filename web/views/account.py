# import random
#
# from django import forms
from django.http import JsonResponse
# from utils.send_email import send_email
from django_redis import get_redis_connection
from django.shortcuts import render, redirect
# 字段进行正则表达式校验
# from django.core.validators import RegexValidator

from web import models
from order_sys import settings
from utils.response import BaseResponse
from web.forms.account import LoginForm, EmailForm, EmailLoginForm


# 用于绕过csrf的导入
# from django.views.decorators.csrf import csrf_exempt

def login(request):
    # 　判断是哪一种请求类型
    if request.method == "GET":
        # 返回html页面，读取html文件并且渲染
        # 在templates里面去找，找根目录下的，在轮回找app里面的
        form = LoginForm()
        return render(request, "login.html", {"form": form})

    print("密码登入测试")

    res = BaseResponse()

    # 1. 接收获取数据（合法性过滤，通过django提供的form和modelform组件完成）
    # 把数据传给他进行对比，格式校验
    form = LoginForm(data=request.POST)
    # 调用这个进行校验
    # 校验失败后的处理
    # 从这里开始校验
    if not form.is_valid():
        # 校验失败后，form内存有之前的提交值，渲染页面是会自动带上
        print("校验失败")
        res.detail = form.errors
        print(res.detail)
        return JsonResponse(res.dict, json_dumps_params={"ensure_ascii": False})

    # 多字段验证
    data_dic = form.cleaned_data

    print("校验成功", data_dic)

    #     # 校验成功通过form.cleaned_data来获取校验成功后的值，是一个字典，能拿取各字段
    # username = form.cleaned_data.get("username")
    # password = form.cleaned_data.get("password")
    role = data_dic.pop("role")
    print("校验成功", data_dic)
    print(role)
    # 2. 进行校验，管理员或客户

    # # 角色不存在的情况，在form中已经校验
    # if role not in mapping.keys():
    #     form.add_error("role", "角色不存在")
    #     return render(request, {"form": form})

    if role == "1":
        print("管理员校验")
        # 进入管理员表查询，需要查询状态是否唯一

        user_obj = models.Administrator.objects.filter(active=1).filter(**data_dic).first()

    else:
        user_obj = models.Customer.objects.filter(active=1).filter(**data_dic).first()
        print(user_obj)
    # 校验失败返回当前页面

    if not user_obj:
        # 没有查询到的，添加错误
        print("校验失败")
        res.detail = {"password": ["用户名或密码错误"]}
        return JsonResponse(res.dict, json_dumps_params={"ensure_ascii": False})
    # 校验成功，从数据库中拿到数据，保存到session中，重定向到后台
    # 把role转化为英文字母，方便到权限字典中查询，session的作用是什么?,user_obj的每个对象都是一行，要在行里面拿数据
    print(1)
    mapping = {"1": "ADMIN", "2": "CUSTOMER"}
    print(2)

    print(type(user_obj), user_obj)

    request.session[settings.NB_SESSION_KEY] = {"role": mapping[role], "username": user_obj.username,
                                                "id": user_obj.id}

    print("数据库检查完成", request.session[settings.NB_SESSION_KEY])

    # 返回要转跳的页面
    # 返回模板
    res = BaseResponse()
    res.status = True
    res.data = settings.HOME_PAGE
    print(1)
    return JsonResponse(res.dict)


# 邮箱登入
def email_login(request):
    # 　判断是哪一种请求类型
    if request.method == "GET":
        # 返回html页面，读取html文件并且渲染
        # 在templates里面去找，找根目录下的，在轮回找app里面的
        # 这里没有校验，只是用于存数据
        form = EmailLoginForm()
        print("发送GET请求")
        return render(request, "email_login.html", {"form": form})
    # 返回模板
    res = BaseResponse()
    # 1. 接收获取数据,提交的表单数据
    print(request.POST)
    print("发送POST请求")
    # 2. 进行校验，利用form
    forms = EmailLoginForm(data=request.POST)
    # 校验不通过返回
    if not forms.is_valid():
        # 设置错误信息
        res.detail = forms.errors
        return JsonResponse(res.dict, json_dumps_params={"ensure_ascii": False})
    # 邮箱验证,用户提交的数据
    email = forms.cleaned_data["email"]
    # code = forms.cleaned_data["code"]
    role = forms.cleaned_data["role"]

    # 缓存验证码校验已经在form里面完成

    # 登入成功 + 注册（一般新邮箱自动注册，已注册自动登入）
    # 这个业务不开放注册，先检测邮箱是否存在，表里面查，应该放到email钩子里面验证
    if role == "1":
        # 进入管理员表查询，需要查询状态是否唯一
        user_obj = models.Administrator.objects.filter(active=1, email=email).first()
    else:
        user_obj = models.Customer.objects.filter(active=1, email=email).first()

    if not user_obj:
        res.detail = {"email": ["邮箱不存在"]}
        return JsonResponse(res.dict)
    mapping = {"1": "ADMIN", "2": "CUSTOMER"}
    # 校验成功，写入session,因为外面还要用这个对象，所以就不写到里面去
    # session默认用两周
    request.session[settings.NB_SESSION_KEY] = {"role": mapping[role], "username": user_obj.username,
                                                "id": user_obj.id}
    res.status = True
    # 返回要转跳的页面
    res.data = settings.HOME_PAGE
    return JsonResponse(res.dict)


# 邮箱登入发送验证请求
# 绕过csrf验证的修饰器，在一些特殊的业务
# @csrf_exempt
def email_send(request):
    '''
    发送邮箱
    :return:
    '''

    # 初始化返回信息
    res = BaseResponse()
    # 1. 邮箱二次校验合法性(后端校验不加，万一出现恶意请求就糟糕了)
    forms = EmailForm(data=request.POST)
    # 合法性校验，发送验证码，报错缓存，爆出异常后直接回在字段下面展示
    if not forms.is_valid():
        print(forms.errors.as_json())
        # 设置错误信息
        res.detail = forms.errors
        return JsonResponse(res.dict, json_dumps_params={"ensure_ascii": False})
    # 3. todo:数据库校验邮箱是否存在

    # 放到form验证里面去了
    # email_ = forms.cleaned_data["email"]
    # role_ = forms.cleaned_data["role"]
    # if role_ == "1":
    #     # 进入管理员表查询，需要查询状态是否唯一
    #     exist = models.Administrator.objects.filter(active=1, email=email_).exists()
    #     # print(1)
    # else:
    #     exist = models.Customer.objects.filter(active=1, email=email_).first()
    #
    # if not exist:
    #     res.detail = {"email": ["邮箱不存在"]}
    #     return JsonResponse(res.dict)

    # email_ = forms.cleaned_data["email"]
    # # 2. 生成验证码，然后发送,是否发送成功处理
    # code = random.randint(1000, 9999)
    # is_send = send_email(email_, code)
    # # 发送失败处理
    # if not is_send[0]:
    #     # 错误信息返回到页面
    #     res.detail = {"email": [is_send[1]]}
    #     return JsonResponse(res.dict,
    #                         json_dumps_params={"ensure_ascii": False})

    # print("ajax请求POST，命中", request.POST.get("email"))
    # # 页面发送ajax请求时不用写HTTP_，会自动拼接，但到这里拿的时候要写全HTTP_
    # # 利用缓存设置有效时间
    # # 链接redis
    # conn = get_redis_connection("default")
    # # 设置值和验证码,ex超时时间60s
    # conn.set(request.POST.get("email"), code, ex=120)

    return JsonResponse({'status': True})


# 主菜单页面
def home(request):
    return render(request, 'home.html')


def logout(request):
    # 清除session
    print(1)
    request.session.clear()
    return redirect(settings.NB_LOGIN_URL)
