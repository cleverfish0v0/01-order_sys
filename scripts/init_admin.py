# 这是离线脚本，用于注册管理员账户

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
django.setup() # 伪造dango启动

# 能导入
from web import models
from utils.encrypt import md5

# models.Administrator.objects.create(
#     username="admin",
#     password=md5("7765894"),
#     email="galh3013@gamil.com"
# )
