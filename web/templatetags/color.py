'''自定义模板语法'''

from django.template import Library
from web import models
register = Library()

@register.filter
def color(num):
    # 拿到样式字典
    return models.TransactionRecord.charge_type_class_mapping[num]
