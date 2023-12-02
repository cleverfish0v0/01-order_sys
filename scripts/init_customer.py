# 这是离线脚本，用于注册用户账号

# 先启动django
# 然后才是运行脚本，但如果是分开启动二者不在一个进程，资源无法共享
import os
import sys
import django

# 根目录路径
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 导入项目路径
sys.path.append(base_dir)

# 将django项目的配置文件路径放入环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_sys.settings')
# 找到环境变量中的配置找到settings
django.setup()  # 伪造dango启动

# 能导入
from web import models
from utils.encrypt import md5

# 用户和用户级别
# 先创建级别
# level_obj = models.level.objects.create(
#     title="vip",
#     percent=90
# )

# models.Customer.objects.create(
#     username="longbatina",
#     password=md5("666"),
#     email="galh3013@gamil.com",
#     user_level_id=1,
#     creator_id=1
# )

# for i in range(1, 302):
#     models.Customer.objects.create(
#         username="用户{}号".format(i),
#         password=md5("666{}".format(i)),
#         email="galh3013@gamil.com",
#         user_level_id=1,
#         creator_id=1
#     )


# for i in range(2):
#     models.Customer.objects.create(
#         username="用户{}号".format(i),
#         password=md5("66666{}".format(i)),0
#         email="galh3013@gamil.com",
#         user_level_id=1,
#         creator_id=1
#     )