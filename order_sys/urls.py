"""order_sys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from web.views import account, level, customer, policy, my_order, my_transaction

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('login/', account.login, name="login"),
    path('email/login/', account.email_login, name="email_login"),
    path('email/send/', account.email_send, name="email_send"),
    path('logout/', account.logout, name="logout"),

    path('home/', account.home, name="home"),

    path('level/list/', level.level_list, name="level_list"),
    path('level/add/', level.level_add, name="level_add"),
    path('level/edit/<int:pk>/', level.level_edit, name="level_edit"),
    path('level/delete/<int:pk>/', level.level_delete, name="level_delete"),

    path('customer/list/', customer.customer_list, name="customer_list"),
    path('customer/add/', customer.customer_add, name="customer_add"),
    path('customer/edit/<int:pk>/', customer.customer_edit, name="customer_edit"),
    # 统一固定参数位置，在最后
    path('customer/reset/<int:pk>/', customer.customer_reset, name="customer_reset"),
    path('customer/delete/', customer.customer_delete, name="customer_delete"),
    # 交易记录
    path('customer/charge/<int:pk>/', customer.customer_charge, name="customer_charge"),
    path('customer/charge/<int:pk>/add/', customer.customer_charge_add, name="customer_charge_add"),

    # 　价格策略
    path('policy/list/', policy.policy_list, name="policy_list"),
    path('policy/add/', policy.policy_add, name="policy_add"),
    path('policy/edit/<int:pk>', policy.policy_edit, name="policy_edit"),
    path('policy/delete/', policy.policy_delete, name="policy_delete"),
    # 带正则表达式的路径,这个表示带一个数字
    re_path(r'policy/(\d+)', policy.policy_delete, name='xxx'),

    # 客户下单
    path('my/order/list/', my_order.my_order_list, name="my_order_list"),
    path('my/order/list/add/', my_order.my_order_list_add, name="my_order_list_add"),
    path('my/order/list/cancel/<int:pk>/', my_order.my_order_list_cancel, name="my_order_list_cancel"),
    # 客户交易记录
    path('my/transaction/list/', my_transaction.my_transaction_list, name="my_transaction_list"),
]
