# 返回数据的格式统一
class Response(object):
    def __init__(self):
        # 默认返回成功
        self.status = True
        self.detail = None
        self.data = None

    # 以字典的形式返回
    def dict(self):
        return self.__dict__


L = Response()
print(L.dict())
