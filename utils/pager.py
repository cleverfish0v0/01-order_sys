'''
以后使用分页
'''
from django.utils.safestring import mark_safe
import copy


class Pagination(object):
    '''
    分页类
    '''

    def __init__(self, request, query_set, per_page_count=10):
        self.query_set = query_set
        # 防止request被污染
        self.query_dict = copy.deepcopy(request.GET)
        # 　设置为可修改
        self.query_dict._mutable = True

        self.page = request.GET.get('page')

        self.per_page_count = per_page_count
        self.total_count = self.query_set.count()

        self.page_count, div = divmod(self.total_count, self.per_page_count)
        if div:
            self.page_count = self.page_count + 1

        if not self.page:
            self.page = 1
        else:
            if not self.page.isdecimal():
                self.page = 1
            else:
                self.page = int(request.GET.get('page'))
                if self.page <= 0:
                    self.page = 1
                elif self.page > self.page_count:
                    self.page = self.page_count
        self.start = (self.page - 1) * self.per_page_count
        self.end = self.page * self.per_page_count

    def html(self):

        # 如果没有数据，不显示菜单
        if not self.query_set:
            return '暂无数据'

        # 总页码小于11
        if self.page_count <= 11:
            start_page = 1
            end_page = self.page_count
        else:
            # 总页码大于11
            # 判断当前页，小于6或小于等于6，固定显示1-11页
            if 0 < self.page <= 6:
                start_page = 1
                end_page = 11
            elif 6 < self.page <= self.page_count - 5:
                start_page = self.page - 5
                end_page = self.page + 5
            elif self.page > self.page_count - 5:
                start_page = self.page_count - 10
                end_page = self.page_count
        # 显示的页码
        page_list = []
        # 首页,添加get请求参数
        self.query_dict.setlist('page', [1])
        # 生成请求首行参数,这么做是为了保存之前的信息
        page_list.append('<li ><a href="?{}">首页</a></li>'.format(self.query_dict.urlencode()))
        if self.page > 1:
            # 修改get参数page,self.page - 1 就是上一页的页码
            self.query_dict.setlist('page', [self.page - 1])
            page_list.append('<li ><a href="?{}">上一页</a></li>'.format(self.query_dict.urlencode()))

        for i in range(start_page, end_page + 1):
            # 添加默认选中
            self.query_dict.setlist('page', [i])
            if i == self.page:
                item = '<li class="active"><a href="?{}">{}</a></li>'.format(self.query_dict.urlencode(), i)
            else:
                item = '<li><a href="?{}">{}</a></li>'.format(self.query_dict.urlencode(), i)
            page_list.append(item)
        if self.page < self.page_count:
            self.query_dict.setlist('page', [self.page + 1])
            page_list.append('<li ><a href="?{}">下一页</a></li>'.format(self.query_dict.urlencode()))
        self.query_dict.setlist('page', [self.page_count])
        page_list.append('<li ><a href="?{}">尾页</a></li>'.format(self.query_dict.urlencode()))
        page_list.append('<li ><a class="disabled" >数据共{}条{}页</a></li>'.format(self.total_count, self.page_count))
        page_string = ''.join(page_list)
        print(page_list)
        return mark_safe(page_string)

    def queryset(self):
        # 防御性编程
        if self.total_count:
            return self.query_set[self.start:self.end]
        return self.query_set

