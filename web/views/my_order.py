import random

from django.db import transaction
from django.shortcuts import render
from web import models
from utils.pager import Pagination
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
from django.db.models import F
from utils.link import filter_reverse
import datetime
from utils.video import get_old_view_count
from django.conf import settings
from django.contrib import messages
from django.contrib.messages.api import get_messages


def my_order_list(request):
    # # 读取之前页面设置的message
    # messages = get_messages(request)
    # for obj in messages:
    #     # 读取同时会删除
    #     print(obj.message)

    # 获取我的订单
    queryset = models.Order.objects.filter(order_customer_id=request.nb_user.id).filter(active=1)
    pager = Pagination(request, queryset)

    return render(request, 'my_order_list.html', {'pager': pager})


# 基于数据库模型生成字段
class MyOrderModelForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = models.Order
        fields = ['url', 'count']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 拿到价格策略
        price_count_list = []
        text_count_list = []
        queryset = models.PriceTactics.objects.all().order_by('count')
        for item in queryset:
            unti_price = item.price / item.count
            price_count_list.append([item.count, '>={} ￥{}/条'.format(item.count, unti_price), unti_price])
            text_count_list.append('>={} ￥{}/条'.format(item.count, unti_price))

        # 没有价格策略联系管理员
        if text_count_list:
            self.fields['count'].help_text = ",".join(text_count_list)
        else:
            self.fields['count'].help_text = '请联系管理员设置价格'
        # 存储
        self.price_count_list = price_count_list

    # 校验
    def clean_count(self):
        count = self.cleaned_data['count']
        # 如果价格策略为空返回
        if not self.price_count_list:
            # 抛出异常
            raise ValidationError('请联系管理员设置价格')
        # 判断是否大于最小数量，self.price_count_list[0][0]，是价格策略的最低档位
        min_count_limit = self.price_count_list[0][0]
        if count < min_count_limit:
            print(count)
            raise ValidationError("最低支持数量为{}".format(min_count_limit))
        return count


def my_order_list_add(request):
    if request.method == 'GET':
        form = MyOrderModelForm()
        # 用于提交判断
        return render(request, 'form.html', {'form': form})
    # 判断是哪一个等级
    form = MyOrderModelForm(data=request.POST)
    if not form.is_valid():
        print('校验失败')
        return render(request, 'form.html', {'form': form})
    print('校验成功')
    # 获取到url和count
    video_url = form.cleaned_data['url']
    count = form.cleaned_data['count']
    # 获取原来播放量
    status, old_view_count = get_old_view_count(video_url)
    if not status:
        form.add_error('url', '视频播放量获取失败')
        return render(request, 'form.html', {'form': form})

    # 1. 根据数量获取单价，计算出原价
    for idx in range(len(form.price_count_list) - 1, -1, -1):
        '''
        前取后不取，后-1不取，取到到0，第三个参数表示倒序取
        倒序方便比较定位
        '''
        limit_count, _, unit_price = form.price_count_list[idx]

        if count >= limit_count:
            break
    total_price = count * unit_price
    print(total_price, type(total_price))
    # 2. 计算出折扣价格，不同会员享受不同价格,链表操作select_related查percent
    try:
        with transaction.atomic():
            # 加事务和锁
            cus_obj = models.Customer.objects.filter(id=request.nb_user.id).select_related(
                "user_level").select_for_update().first()
            # 链表查询这么拿数据cus_obj.user_level.percent，用联表字段
            print(cus_obj.user_level.percent, type(cus_obj.user_level.percent))

            real_price = total_price * cus_obj.user_level.percent / 100
            print(real_price, type(real_price))

            # 3. 判断账户余额够不够
            print(cus_obj.balance, type(cus_obj.balance))
            if cus_obj.balance < real_price:
                form.add_error('count', '账户余额不足请进行充值')
                return render(request, 'form.html', {'form': form})
            # 4. 创建订单
            # 4.1 生成订单号,唯一，时间戳
            while True:
                rand_number = random.randint(10000000, 99999999)
                ctime = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                cid = "{}{}".format(ctime, rand_number)
                # 判断订单号是否已经存在
                exists = models.Order.objects.filter(cid=cid).exists()
                if exists:
                    continue
                break

            # 4.2 爬虫发送网络请求,获取播放量
            # 不放到事务的锁里
            print('原播放', old_view_count)
            # 4.3 客户ID等于当前登录客户的ID
            form.instance.cid = cid
            form.instance.price = total_price
            form.instance.real_price = real_price
            form.instance.old_view_count = old_view_count
            form.instance.order_customer_id = request.nb_user.id
            form.save()
            # 5. 账户扣款，锁
            models.Customer.objects.filter(id=request.nb_user.id).update(balance=F('balance') - real_price)
            # 6. 生成交易记录
            models.TransactionRecord.objects.create(
                charge_type=3,
                trade_customer_id=request.nb_user.id,
                amount=real_price,
                order_cid=cid
            )
            # 7. 写入队列，等待worker工作
            from django_redis import get_redis_connection
            conn = get_redis_connection('default')
            conn.lpush(settings.QUEUE_TASK_NAME, cid)
    except Exception as e:
        form.add_error('count', '创建订单失败')
        return render(request, 'form.html', {'form': form})
    # 要考虑事务，锁（扣款）

    return redirect('my_order_list')


def my_order_list_cancel(request, pk):
    '''撤单'''
    order_object = models.Order.objects.filter(id=pk, active=1, status=1, order_customer_id=request.nb_user.id).first()
    if not order_object:
        messages.add_message(request, messages.WARNING, '订单不存在')
        return redirect('my_order_list')

    try:
        with transaction.atomic():
            # 加事务和锁
            cus_obj = models.Customer.objects.filter(id=request.nb_user.id).select_for_update().first()
            # 1. 订单状态改变为(5, "已撤单")
            models.Order.objects.filter(id=pk, active=1, status=1, order_customer=request.nb_user.id).update(status=5)
            # 2. 归还余额
            models.Customer.objects.filter(id=request.nb_user.id).update(balance=F('balance') + order_object.real_price)
            # 3. 交易记录
            models.TransactionRecord.objects.create(
                charge_type=5,
                trade_customer_id=request.nb_user.id,
                amount=order_object.real_price,
                order_cid=order_object.cid
            )

        # 撤单成功后
        messages.add_message(request, messages.SUCCESS, '撤单成功')
        # 写入后就是一个列表，下次要进行读取,在my_order_list
        return redirect('my_order_list')
    except Exception as e:
        messages.add_message(request, messages.WARNING, '撤单失败')
        return redirect('my_order_list')

