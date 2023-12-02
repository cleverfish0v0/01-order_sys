'''自定义模板语法'''

from django.template import Library
from django.conf import settings
import copy

register = Library()


@register.inclusion_tag("tag/nb_menu.html")
def nb_menu(request):

    # 1. 读取当前用户的角色信息，request里面存有
    print(request.nb_user.role)
    # 2. 获取菜单信息
    user_menu_list = copy.deepcopy(settings.NB_MENU[request.nb_user.role])
    # 默认菜单选中
    for item in user_menu_list:
        # 默认父级置空
        item['class'] = 'hide'
        for child in item['children']:
            # if child["url"] == request.path_info:
            if child["name"] == request.nb_user.menu_name:
                child['class'] = 'active'
                item['class'] = ''

    return {"menu_list": user_menu_list}
