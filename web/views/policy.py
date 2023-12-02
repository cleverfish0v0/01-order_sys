from django.shortcuts import render, redirect
from web import models
from utils.pager import Pagination
# 创造字段用于表单，form里面有modelform
from django import forms
from utils.bootstrap import BootstrapForm
from utils.response import BaseResponse
from django.http import JsonResponse


def policy_list(request):
    '''这个业务并不需要菜单,直接传递对象'''

    queryset = models.PriceTactics.objects.all().order_by('count')
    pager = Pagination(request, queryset)
    return render(request, 'policy_list.html', {'pager': pager})


# 字段
class PolicyModelForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = models.PriceTactics
        fields = '__all__'


def policy_add(request):
    if request.method == 'GET':
        form = PolicyModelForm()
        return render(request, 'form(02).html', {'form': form})
    # 上传验证参数
    form = PolicyModelForm(data=request.POST)
    if not form.is_valid():
        return render(request, 'form(02).html', {'form': form})
    form.save()
    return redirect('/policy/list/')


def policy_edit(request, pk):
    # 指定行修改
    instance = models.PriceTactics.objects.filter(id=pk).first()
    if request.method == 'GET':
        form = PolicyModelForm(instance=instance)
        return render(request, 'form(02).html', {'form': form})

    # POST提交处理。update，data=request.POST是要校验这些数据
    form = PolicyModelForm(instance=instance, data=request.POST)
    # 进行校验
    if not form.is_valid():
        print('校验失败', form.errors)
        return render(request, 'form(02).html', {'form': form})
    # 同过校验后保存
    form.save()
    return redirect('/policy/list/')


def policy_delete(request):
    res = BaseResponse()
    # 不存在就置零
    cid = request.GET.get('cid', 0)
    if not cid:
        res.detail = '请选择要删除的数据'
        return JsonResponse(res.dict)

    exists = models.PriceTactics.objects.filter(id=cid).exists()
    if not exists:
        res.detail = '数据不存在'
        return JsonResponse(res.dict)

    models.PriceTactics.objects.filter(id=cid).delete()
    # 返回
    res.status = True
    res.url = '/policy/delete/'
    return JsonResponse(res.dict)
