from django.db.models import Q
from django.shortcuts import render
from web import models
from utils.pager import Pagination
from utils.group import Option,get_search_group_condition


def my_transaction_list(request):
    '''我的交易记录'''

    search_group = [
        Option('charge_type'),
    ]

    search_group_row_list = []
    for option_object in search_group:
        row = option_object.get_queryset_or_tuple(models.TransactionRecord,request)
        search_group_row_list.append(row)
    # 构造搜索调价你
    conn = get_search_group_condition(search_group,request)

    # 拿到搜索关键字
    keyword = request.GET.get('keyword', '').strip()

    con = Q()
    if keyword:
        # 构造搜索条件
        con.connector = 'OR'
        con.children.append(('order_cid__contains', keyword))

    queryset = models.TransactionRecord.objects.filter(con).filter(**conn).filter(trade_customer_id=request.nb_user.id, active=1)

    pager = Pagination(request, queryset)
    # 生成页面
    context = {
        'pager': pager,
        'keyword': keyword,
        'search_group_row_list': search_group_row_list,
    }

    return render(request, 'my_transaction_list.html', context)
