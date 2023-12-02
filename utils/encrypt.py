# 用于加密的模块

import hashlib
from order_sys.settings import SECRET_KEY


def md5(date_string):
     # 参数二进制加密
    obj = hashlib.md5(SECRET_KEY.encode("UTF-8"))
    obj.update(date_string.encode("utf-8"))
    # 返回对象加密的值
    return obj.hexdigest()
