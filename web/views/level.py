from django.shortcuts import render, redirect
from web import models
from django import forms
from utils.bootstrap import BootstrapForm


# class LevelForm(BootstrapForm, forms.Form):
#     title = forms.CharField(
#         label="标题",
#         required=True,
#     )
#     percent = forms.CharField(
#         label="折扣",
#         required=True,
#         help_text="填入0-100整数表示百分比，例如：90，表示90%"
#     )


# 作用是？
class LevelModeForm(BootstrapForm, forms.ModelForm):
    # 自动按照顺序执行，继承关系的初始化方法
    class Meta:
        model = models.level
        fields = ['title', 'percent']


# 查询客户等级表
def level_list(request):
    # 查询等级表中激活的部分
    queryset = models.level.objects.filter(active=1)
    return render(request, 'level_list.html', {'queryset': queryset})


def level_add(request):
    # 添加请求
    if request.method == "GET":
        form = LevelModeForm()
        return render(request, 'form.html', {'form': form})
    # 校验数据后直接保存,上传响应头
    form = LevelModeForm(data=request.POST)
    # 进行校验
    if not form.is_valid():
        # 失败后返回页面，错误信息会自动显示
        print(form.errors)
        return render(request, 'form.html', {'form': form})
    # 用这个能直接保存到数据库
    form.save()
    return redirect('level_list')


def level_edit(request, pk):
    level_object = models.level.objects.filter(id=pk).first()
    if request.method == "GET":
        # 参数initial上传字典，设置字段默认值
        # 通过字段传入,无法返回默认值
        print(level_object.title, level_object.percent)
        form = LevelModeForm(instance=level_object)
        return render(request, 'form.html', {'form': form})

    # 带入当前数据，根性当前行

    # 获取数据 + 校验
    print('保存到')
    form = LevelModeForm(data=request.POST, instance=level_object)
    if not form.is_valid():
        # print('校验失败', form.errors)
        return render(request, 'form.html', {'form': form})
    # 根据ID提交数据，更新，使用form
    # models.level.objects.filter(id=pk).update(title='',percent='')
    # 使用form.save会新增
    form.save()
    return redirect('level_list')


# 逻辑删除
def level_delete(request, pk):
    # 查询当前等级下是否还有客户,跨表查询
    exists = models.Customer.objects.filter(user_level_id=pk).exists()
    if not exists:
        models.level.objects.filter(id=pk).update(active=0)

    return redirect('level_list')
