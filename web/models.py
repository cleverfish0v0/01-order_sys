from django.db import models
import datetime


# Create your models here.

# 字段继承
class ActiveBaseModel(models.Model):
    '''
    这张表不生成，是基类
    '''
    # 逻辑删除
    active = models.SmallIntegerField(verbose_name="状态", default=1, choices=((1, "激活"), (0, "已删除")))

    class Meta:
        # 不建立表结构
        abstract = True


class Administrator(ActiveBaseModel):
    """管理员表"""
    # db_index创建索引
    username = models.CharField(verbose_name="用户名", max_length=32, db_index=True)
    password = models.CharField(verbose_name="密码", max_length=64)
    email = models.CharField(verbose_name="邮箱", max_length=44, db_index=True)
    # 两个字段功能不同，auto_now字段设置为True则创建或更新时时期会改变，auto_now_add则只保存创建日期，两个字段都可以加
    creat_date = models.DateTimeField(verbose_name="创建日期", auto_now_add=True)

    # 设置管理员状态，这是逻辑上的删除，不是物理上的删除
    # 1 激活
    # 0 已删除
    # 使用choice，条件显示
    # active = models.SmallIntegerField(verbose_name="状态", default=1, choices=((1, "激活"), (0, "已删除")))

    def __str__(self):
        return self.username


# # 查询使用,返回属于行数据对象
# data = Administrator.objects.all()
# # 循环拿到每一行
# for item in data:
#     item.username
#     ...
#     # 显示对应的值
#     item.get_active_display()


# 客户等级表
class level(ActiveBaseModel):
    """客户等级表"""
    title = models.CharField(verbose_name="标题", max_length=32)
    percent = models.IntegerField(
        verbose_name="折扣",
        help_text="（请输入0-100的整数表示百分比。例如：90表示90%）",

    )

    # # 逻辑删除
    # active = models.SmallIntegerField(verbose_name="状态", default=1, choices=((1, "激活"), (0, "已删除")))

    # 调用对象，返回字段
    def __str__(self):
        return f'{self.title}({self.percent})'


# 客户表
class Customer(ActiveBaseModel):
    """客户表，管理员和用户表字段相同可以放在相同的表"""
    # db_index创建索引，
    # TODO:用户名和密码应该是联合唯一索引，用户名在前面，索引能命中查询用户名是否存在
    username = models.CharField(verbose_name="用户名", max_length=32, db_index=True)
    password = models.CharField(verbose_name="密码", max_length=64)
    email = models.CharField(verbose_name="邮箱", max_length=44, db_index=True)

    # 账户余额
    # max_digits ,允许最大位数；decimal_places 最小最大位数，小数点后2位 3
    balance = models.DecimalField(verbose_name="账户余额", default=0, max_digits=10, decimal_places=2)
    # # 客户等级
    # # 1. 如果就固定那几个级别不用更改
    # level_list = ((0, "vip"), (1, "svip"), (2, "ssvip"))
    # level = models.SmallIntegerField(verbose_name="状态", default=1, choices=level_list)
    # # 2. 如果需要随时改变，则需要重新创建客户等级表

    # 外键链接客户等级，通过verbose_name进行外键链接,to是链接的表名，on_delete是删除模式，models.CASCADE级联删除，等级没了数据也没了,limit_choices_to,自动筛选的条件,跨表找active为1的数据，如id__gt:2,id大于2
    # user_level = models.ForeignKey(verbose_name="折扣", to=level, on_delete=models.CASCADE, null=True, blank=True,limit_choices_to={'active': 1})
    user_level = models.ForeignKey(verbose_name="折扣", to=level, on_delete=models.CASCADE, null=True, blank=True)

    # # 逻辑删除
    # active = models.SmallIntegerField(verbose_name="状态", default=1, choices=((1, "激活"), (0, "已删除")))

    # 邀请制度，邀请人字段，就是外键绑定管理员
    creator = models.ForeignKey(verbose_name="创建者", to=Administrator, on_delete=models.CASCADE)
    # 创建日期
    creat_date = models.DateTimeField(verbose_name="创建日期", auto_now_add=True, null=True, blank=True)


# 价格策略表
class PriceTactics(models.Model):
    """价格策略，物理删除，多少数量有多少数量的价格
    1000 10
    2000 10

    """

    count = models.IntegerField(verbose_name="数量")
    price = models.DecimalField(verbose_name="价格", default=0, max_digits=10, decimal_places=2)


# 订单表
class Order(ActiveBaseModel):
    """订单表"""
    status_choice = (
        (1, "待执行"),
        (2, "正在执行"),
        (3, "已完成"),
        (4, "失败"),
        (5, "已撤单")
    )
    # 状态
    status = models.SmallIntegerField(verbose_name="订单状态", choices=status_choice, default=1)

    # 订单唯一标识，订单号
    cid = models.CharField(verbose_name="订单号", max_length=64, unique=True)
    url = models.URLField(verbose_name="视屏链接", db_index=True)

    # 下单数量
    count = models.IntegerField(verbose_name="数量")
    # # 不能进行全部关联，如果修改，之前的帐也会变
    # policy = models.ForeignKey(verbose_name="价格", to=PriceTactics,on_delete=)
    # 原价
    price = models.DecimalField(verbose_name="价格", default=0, max_digits=10, decimal_places=2)

    # 实际价格（会员等级打折）
    real_price = models.DecimalField(verbose_name="实际价格", default=0, max_digits=10, decimal_places=2)

    # 关联客户
    order_customer = models.ForeignKey(verbose_name="客户", to=Customer, on_delete=models.CASCADE)
    # 创建时间
    creat_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    # 备注信息
    remark = models.TextField(verbose_name="备注", null=True, blank=True)

    # 原播放量
    old_view_count = models.CharField(verbose_name="原播放量", max_length=32, default=0)


# 交易记录表
class TransactionRecord(ActiveBaseModel):
    """交易记录"""
    # 设置bootstrap样式,用于按钮渲染
    charge_type_class_mapping = {
        1: "success",
        2: "danger",
        3: "default",
        4: "info",
        5: "primary"
    }

    charge_type_choice = ((1, "充值"), (2, "扣款"), (3, "创建订单"), (4, "删除订单"), (5, "撤单"))
    charge_type = models.SmallIntegerField(verbose_name="类型", choices=charge_type_choice)

    # 客户
    trade_customer = models.ForeignKey(verbose_name="客户", to="Customer", on_delete=models.CASCADE)
    # 充值
    amount = models.DecimalField(verbose_name="金额", default=0, max_digits=10, decimal_places=2)
    # 管路员,可为空（主要针对充值，扣款），有些操作不需要管理员
    creator = models.ForeignKey(verbose_name="管理员", to="Administrator", on_delete=models.CASCADE, null=True, blank=True)
    # 操作的订单，针对创建订单，删除订单，撤单，记录订单号，通过订单号来查找订单信息
    # order = models.ForeignKey(verbose_name="订单号", to="Order", on_delete=models.CASCADE, null=True, blank=True)
    # 需要通过订单号索引
    order_cid = models.CharField(verbose_name="订单号", max_length=64, null=True, blank=True, db_index=True)
    # 备注信息
    remark = models.TextField(verbose_name="备注", null=True, blank=True)

    # 创建日期
    creat_date = models.DateTimeField(verbose_name="创建日期", auto_now_add=True, null=True, blank=True)
