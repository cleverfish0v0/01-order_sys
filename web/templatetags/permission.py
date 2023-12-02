'''自定义模板语法'''
# QueryDict是request的对象
from django.http import QueryDict

from django.template import Library
from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe

register = Library()


def check_permission(request, name):
    # 1. 获取当前登入用户的角色
    role = request.nb_user.role
    # 2. 根据角色获取他所有的权限字典
    permission_dict = settings.NB_PERMISSION[role]
    if name in permission_dict:
        # 无权访问，返回空
        return True
    # 公共权限
    if name in settings.NB_PERMISSION_PUBLIC:
        return True


# 模版语言，选择sample_tag是因为返回空方便（没有权限时）

@register.simple_tag
def add_permission(request, name, *args, **kwargs):
    if not check_permission(request, name):
        return ''
    # 4. 有权限生成按键，无权限返回空字符串，通过名字反向生成url
    url = reverse(name, args=args, kwargs=kwargs)
    upl = '''
     <a class="btn btn-success" href="{}"><i class="bi bi-apple"></i>新建</a>
    '''.format(url)

    return mark_safe(upl)


@register.simple_tag
def edit_permission(request, name, *args, **kwargs):
    if not check_permission(request, name):
        return ''
    # 4. 有权限生成按键，无权限返回空字符串，通过名字反向生成url
    url = reverse(name, args=args, kwargs=kwargs)

    # 获取按钮前，截取当前页面参数
    param = request.GET.urlencode()
    if param:
        new_query_dict = QueryDict(mutable=True)
        new_query_dict['_filter'] = param

        print(new_query_dict)
        # 参数转化为字符串
        param_string = new_query_dict.urlencode()

        tpl = '''
         <a href="{}?{}" class="btn btn-primary btn-xs">编辑</a>
         '''.format(url, param_string)

        return mark_safe(tpl)
    tpl = '''
             <a href="{}" class="btn btn-primary btn-xs">编辑</a>
             '''.format(url)
    return mark_safe(tpl)


@register.simple_tag
def delete_permission(request, name, *args, **kwargs):
    if not check_permission(request, name):
        return ''
    # 4. 有权限生成按键，无权限返回空字符串，通过名字反向生成url
    upl = '''
     <a cid="{}" class="btn btn-danger btn-xs btn-delete">删除</a>
    '''.format(kwargs.get('pk'))

    return mark_safe(upl)
