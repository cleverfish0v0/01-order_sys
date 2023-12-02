'''
用于返回类型的封装，json
'''


# 返回数据的格式统一,用于ajax请求返回的格式
class BaseResponse(object):
    def __init__(self):
        # 默认返回失败
        self.status = False
        self.detail = None
        self.data = None
        self.url = None

    # 以字典的形式返回
    @property
    def dict(self):
        return self.__dict__
