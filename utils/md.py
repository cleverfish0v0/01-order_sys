"""
自定义中间件，用于校验是否已经登入，有没有访问权限
"""
from django.shortcuts import redirect, HttpResponse, render
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

from order_sys import settings


class UserInfo(object):
    def __init__(self, role, username, id):
        self.role = role
        self.username = username
        self.id = id
        self.menu_name = None
        self.text_list = None


class AuthMiddleware(MiddlewareMixin):
    # 判断是否登入，并保存登入数据（需要登入的路由才进行判断检验）
    def process_request(self, request):
        '''校验是否已近登入'''
        # 1. 排除不需要登入就能访问的url,request.path_info获取当前访问的url
        if request.path_info in settings.NB_WHITE_URL:
            print("进入：", request.path_info)
            # 返回继续往后
            return

        print("判断是否登入：", request.path_info)
        # 2. session中获取用户信息，获取到就是已经登入，未登入跳转,判断是否登入
        # 已经登入的用户信息存在session里面，字典

        user_dict = request.session.get(settings.NB_SESSION_KEY)

        print(user_dict)
        # 未登入
        if not user_dict:
            return redirect(settings.NB_LOGIN_URL)
        # 已登入，返回用户信息
        # request.user_dict = user_dict

        # 为了方便自动提示，能点出来，就写一个类,创建对象
        request.nb_user = UserInfo(**user_dict)
        print(request.nb_user.username)

    # 判断是否有权限访问（公共权限不用进行）
    def process_view(self, request, callback, callback_args, callback_kwargs):
        print(request.path_info, '权限判断')
        # 无需登入无需权限的，放过
        if request.path_info in settings.NB_WHITE_URL:
            print(request.path_info, '无需权限')
            # 返回继续往后
            return
        # 拿到当前的url名字
        current_name = request.resolver_match.url_name
        # 判断是否为，需要登入，公共权限的
        if current_name in settings.NB_PERMISSION_PUBLIC:
            print(request.path_info, '公共权限')
            return
        # 权限校验
        # 1. 根据用户角色获取自己具备所有的权限,总的权限列表
        user_permission_dic = settings.NB_PERMISSION[request.nb_user.role]
        # 2. 获取当前用户访问的URL,能拿到url的名字
        current_name = request.resolver_match.url_name
        # 3. 判断是否在自己具备的权限
        if current_name not in user_permission_dic:

            print(request.path_info, '有没有权限')
            # 　获取请求头
            if request.is_ajax():
                return JsonResponse({'status': False, 'detail': '无权访问'})
            else:
                # 不存在返回
                return render(request, 'permission.html')
        # 存储路径
        text_list = []
        # 保存当前的路径文本
        text_list.append(user_permission_dic[current_name]['text'])
        # 有权限去找父级,溯源到根路由，看是否有根路由权限
        menu_name = current_name
        while user_permission_dic[menu_name]['parent']:
            print(7)
            # 没有父级就不走这,有就循环的找父级
            menu_name = user_permission_dic[menu_name]['parent']
            # 添加上面的路径文本
            text_list.append(user_permission_dic[menu_name]['text'])
        print(8)
        text_list.append("首页")
        # 翻转列表,生成路径导航列表
        text_list.reverse()
        print(9)
        # 当前菜单
        request.nb_user.menu_name = menu_name
        # 路径导航
        request.nb_user.text_list = text_list
        print(text_list)

        return None
