import re
from django.shortcuts import render, redirect
from web import models
from django import forms
from utils.bootstrap import BootstrapForm
from django.core.exceptions import ValidationError
from utils.encrypt import md5
from django.http import JsonResponse
from utils.response import BaseResponse
from utils.pager import Pagination
from django.db.models import Q
from utils.link import filter_reverse

from utils.group import Option, NbSearchGroup


def customer_list(request):
    search_group = NbSearchGroup(
        request,
        models.Customer,
        Option('user_level', db_condition={"active": 1})  # fk
    )

    # 1.1 获取用户列表
    # 1.2 客户可以被逻辑删除
    # 1.3 级别被删了，下属客户怎么办？（因为是逻辑删除，客户还存着）
    # 思路1，修改级别删除的逻辑，先查询是否有关联数据，没有关联时就删，有关联就不行
    # 思路2，修改为默认值
    # 思路3，不做任何改变，查找客户时，跨表查找等级激活的客户

    # 需要主动联表，否则会多次查询
    # queryset = models.Customer.objects.filter(active=1)

    # 要分页给数据，通过url的参数获取页码,用于切片拿取数据
    # 计算页码数

    # 拿到搜索关键字

    keyword = request.GET.get('keyword', '').strip()

    con = Q()
    if keyword:
        # 构造搜索条件
        con.connector = 'OR'
        con.children.append(('username__contains', keyword))
        con.children.append(('email__contains', keyword))
        con.children.append(('user_level__title__contains', keyword))

    queryset = models.Customer.objects.filter(con).filter(**search_group.get_condition).filter(active=1).select_related(
        'user_level', 'creator')
    if queryset:
        obj = Pagination(request, queryset)

        # 外键返回跨表行对象，models里面去对于表添加__str__方法
        context = {
            # 超出范围后取值为空
            "queryset": queryset[obj.start:obj.end],
            # 用这个包裹后就能在游览器上渲染
            "page_string": obj.html(),
            "keyword": keyword,
            "search_group": search_group
        }

        return render(request, 'customer_list.html', context)
    else:
        context = {
            # 超出范围后取值为空
            "queryset": [],
            # 用这个包裹后就能在游览器上渲染
            "page_string": '内容为空',
            "keyword": keyword,
            "search_group": search_group
        }

        return render(request, 'customer_list.html', context)


class CustomerModelForm(BootstrapForm, forms.ModelForm):
    exclude_filed_list = ['user_level']
    # 重复密码字段
    confirm_password = forms.CharField(
        label='重复密码',
        # 保留密码render_value=True
        widget=forms.PasswordInput(render_value=True)
    )

    # 创建password字段也会覆盖

    class Meta:
        model = models.Customer
        fields = ['username', 'email', 'password', 'confirm_password', 'user_level']
        # 补充添加密码字段插件
        widgets = {
            'password': forms.PasswordInput(render_value=True),
            # 添加字段属性
            'user_level': forms.RadioSelect(attrs={"class": 'form-redid'})
        }

    # 重写初始化方法，添加request接收
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # request里的数据作为条件筛选
        # 外键跨表查询，这个字段决定了显示的内容
        self.fields['user_level'].queryset = models.level.objects.filter(active=1)

    # 钩子方法
    def clean_email(self):
        email = self.cleaned_data['email']
        if not re.match(r"^([a-zA-Z]|[0-9])(\w|\-)+@[a-zA-Z0-9]+\.([a-zA-Z]{2,4})$", email):
            raise ValidationError('邮箱格式错误')
        return email

    # # 这个有先后顺序，前面的拿不到后面的值
    # def clean_password(self):
    #     password = md5(self.cleaned_data['password'])
    #     if password != md5(self.cleaned_data['confirm_password']):
    #         raise ValidationError('重复密码不一致')
    #     return password

    # 这个有先后顺序，前面的拿不到后面的值
    def clean_confirm_password(self):
        confirm_password = self.cleaned_data['confirm_password']
        if confirm_password != self.cleaned_data['password']:
            raise ValidationError('重复密码不一致')
        return confirm_password

    def clean_user_level(self):
        user_leve = self.cleaned_data['user_level']
        # 选择为空
        if not user_leve:
            raise ValidationError('请选择一个级别')
        # 这里应该保存对应的id
        return user_leve


def customer_add(request):
    if request.method == 'GET':
        # 可传request到上面的__init__方法里面
        form = CustomerModelForm(request)
        return render(request, 'form(02).html', {'form': form})

    # POST进行表单验证
    form = CustomerModelForm(request, data=request.POST)
    print('POST请求')
    # 校验不通过返回
    if not form.is_valid():
        print('校验失败', form.errors)
        return render(request, 'form(02).html', {'form': form})
    print('校验通过')
    # 保存数据，修改管理者id，在nb_user里面拿
    form.instance.creator_id = request.nb_user.id
    # 只有这样才能修改保存的值
    form.instance.password = md5(form.cleaned_data['password'])
    form.save()
    return redirect('/customer/list/')


class CustomerEditModelForm(BootstrapForm, forms.ModelForm):
    exclude_filed_list = ['user_level']

    # 创建password字段也会覆盖

    class Meta:
        model = models.Customer
        fields = ['username', 'email', 'user_level']
        # 补充添加密码字段插件
        widgets = {
            # 添加字段属性
            'user_level': forms.RadioSelect(attrs={"class": 'form-redid'})
        }

    # 重写初始化方法，添加request接收
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # request里的数据作为条件筛选
        # 外键跨表查询，这个字段决定了显示的内容
        self.fields['user_level'].queryset = models.level.objects.filter(active=1)

    # 钩子方法,更改邮箱需要验证邮箱有效性
    def clean_email(self):
        email = self.cleaned_data['email']
        if not re.match(r"^([a-zA-Z]|[0-9])(\w|\-)+@[a-zA-Z0-9]+\.([a-zA-Z]{2,4})$", email):
            raise ValidationError('邮箱格式错误')
        return email

    # # 这个有先后顺序，前面的拿不到后面的值
    # def clean_password(self):
    #     password = md5(self.cleaned_data['password'])
    #     if password != md5(self.cleaned_data['confirm_password']):
    #         raise ValidationError('重复密码不一致')
    #     return password

    def clean_user_level(self):
        user_leve = self.cleaned_data['user_level']
        # 选择为空
        if not user_leve:
            raise ValidationError('请选择一个级别')
        # 这里应该保存对应的id
        return user_leve


def customer_edit(request, pk):
    # 指定行修改
    instance = models.Customer.objects.filter(id=pk, active=1).first()
    if request.method == 'GET':
        form = CustomerEditModelForm(request, instance=instance)
        return render(request, 'form(02).html', {'form': form})
    # POST提交处理。update，data=request.POST是要校6验这些数据
    form = CustomerEditModelForm(request, instance=instance, data=request.POST)
    # 进行校验
    if not form.is_valid():
        print('校验失败', form.errors)
        return render(request, 'form(02).html', {'form': form})
    # 同过校验后保存
    form.save()

    return redirect(filter_reverse(request, '/customer/list/'))


class CustomerResetModelForm(BootstrapForm, forms.ModelForm):
    confirm_password = forms.CharField(
        label='重置密码',
        # render_value=True是保存密码，不刷新掉
        widget=forms.PasswordInput(render_value=True)
    )

    # 创建password字段也会覆盖

    class Meta:
        model = models.Customer
        fields = ['password', 'confirm_password']
        # 补充添加密码字段插件
        widgets = {
            'password': forms.PasswordInput(render_value=True)
        }

    # 这个有先后顺序，前面的拿不到后面的值
    def clean_confirm_password(self):
        confirm_password = md5(self.cleaned_data['confirm_password'])
        if confirm_password != md5(self.cleaned_data['password']):
            raise ValidationError('重复密码不一致')
        return confirm_password


def customer_reset(request, pk):
    if request.method == 'GET':
        # 不上传显示默认密码，输入原先密码是否一致，相同才允许修改
        form = CustomerResetModelForm()
        return render(request, 'form(02).html', {'form': form})
    # 要校验的字段，查的原来的数据
    instance = models.Customer.objects.filter(id=pk, active=1).first()
    # data是输入过来的数据
    form = CustomerResetModelForm(data=request.POST, instance=instance)
    if not form.is_valid():
        return render(request, 'form(02).html', {'form': form})
    form.save()

    return redirect('customer_list')


def customer_delete(request):
    res = BaseResponse()
    # 不存在就置零
    cid = request.GET.get('cid', 0)
    if not cid:
        res.detail = '请选择要删除的数据'
        return JsonResponse(res.dict)

    exists = models.Customer.objects.filter(id=cid, active=1).exists()
    if not exists:
        res.detail = '数据不存在'
        return JsonResponse(res.dict)

    models.Customer.objects.filter(id=cid, active=1).update(active=0)
    # 返回
    res.status = True
    return JsonResponse(res.dict)


# 创建表单
class ChargeModelForm(BootstrapForm, forms.ModelForm):
    # 重写字段
    # 使用这种会把int变成字符串，就是那个choices
    # charge_type = forms.ChoiceField(
    #     label='类型',
    #     choices=[(1, '充值'), (2, '扣款')], # 适合固定数据，不适合数据库表里面拿数据，数据库改了就会出问题，设置的静态变量，启动是加载到内存中，与数据库隔离
    #     required=True
    # coerce=int
    # )

    class Meta:
        model = models.TransactionRecord
        fields = ['charge_type', 'amount']

    # 构造方法
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 只能是1或2
        self.fields['charge_type'].choices = [(1, '充值'), (2, '扣款')]


def customer_charge(request, pk):
    '''交易记录,pk为客户id'''

    # trade_customer_id
    # 客户存在，交易记录存在，外键查询强制链表.select_related(‘表名’)
    queryset = models.TransactionRecord.objects.filter(trade_customer_id=pk, trade_customer__active=1,
                                                       active=1).order_by('-id')
    # 所有数据，分页展示

    pager = Pagination(request, queryset)

    # 外键返回跨表行对象，models里面去对于表添加__str__方法
    # 生成表单
    form = ChargeModelForm()
    # 拿去局部变量所有的值
    print(locals())
    return render(request, 'customer_charge.html', {'pager': pager, 'form': form, 'pk': pk})


def customer_charge_add(request, pk):
    print(pk)
    print(request.POST)
    # 创建表单进行校验
    form = ChargeModelForm(data=request.POST)
    if not form.is_valid():
        res = {
            'status': False,
            'detail': form.errors
        }
        return JsonResponse(res)
    # 校验成功，进行更新
    amount = form.cleaned_data['amount']
    charge_type = form.cleaned_data['charge_type']
    # 　进行事务操作
    from django.db import transaction
    try:
        with transaction.atomic():
            # 添加锁select_for_update()，排它锁 # 1. 登入账户对用户进行操作，账户：增加或减少
            cus_obj = models.Customer.objects.filter(id=pk, active=1).select_for_update().first()
            # 事务结束，锁就结束

            # 判断金额和余额大小,账户余额不足的情况
            if charge_type == 2 and cus_obj.balance < amount:
                res = {
                    'status': False,
                    'detail': {'amount': ['余额不足，账户只有：{}'.format(cus_obj.balance)]}
                }
                return JsonResponse(res)

            if charge_type == 1:
                cus_obj.balance = cus_obj.balance + amount
            else:
                cus_obj.balance = cus_obj.balance - amount
            # 更新
            cus_obj.save()
            # 2. 生成交易记录
            form.instance.trade_customer = cus_obj
            form.instance.creator_id = request.nb_user.id
            # 保存表单
            form.save()
    except Exception as e:
        res = {
            'status': False,
            'detail': {'amount': ['操作失败：{}'.format(e)]}
        }
        return JsonResponse(res)
    res = {
        'status': True,
    }
    return JsonResponse(res)
