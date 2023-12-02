import random
from django import forms
# 字段进行正则表达式校验
from django.core.exceptions import ValidationError
from django_redis import get_redis_connection
from django.core.validators import RegexValidator

from web import models
from utils.encrypt import md5
from utils.send_email import send_email


# 定义一个类

class LoginForm(forms.Form):
    # 要校验的数据
    role = forms.ChoiceField(
        # 这个字段必须要有，不能为空
        # required=True,  # 不为空时改为False就行
        label="角色",
        choices=(("1", "管理员"), ("2", "客户")),
        # 可写正则表达式
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "role",
                "name": "role"
            }
        ))

    # 调用form的模板生成html
    username = forms.CharField(
        # 这个字段必须要有，不能为空
        # required=True,
        label="用户名",
        widget=forms.TextInput(
            attrs={"class": "form-control",
                   "placeholder": "输入用户名",
                   "id": "username",
                   "name": "username"
                   }
        ))
    password = forms.CharField(
        # 这个字段必须要有，不能为空
        # 内部默认就不能为空
        # required=True,
        # label字段，能。出来
        label="密码",
        validators=[RegexValidator(r'^[0-9]+$', '密码必须是数字')],
        widget=forms.PasswordInput(
            attrs={"class": "form-control",
                   "placeholder": "输入密码",
                   "id": "password",
                   "name": "password"
                   }
        )
    )

    # 内部执行，抛出异常或返回原来的值
    def clean_username(self):
        # 获取上一次的返回值
        user = self.cleaned_data["username"]
        # 校验规则
        # 校验失败
        if len(user) < 3:
            # 抛出异常
            from django.core.exceptions import ValidationError
            raise ValidationError("用户名过短（小于三位）")
        # 返会重新赋值给self.cleaned_data["username"]
        return user

    # 对所有值进行校验，不能轻易返回值，下次使用时会用这次返回的值
    # 无论前面的校验是否执行都会执行，使用取的self.cleaned_data不一定对

    def clean_password(self):
        password = md5(self.cleaned_data["password"])
        return password


# 生成标签，提交表单之后的校验，走中间件
class EmailLoginForm(forms.Form):
    role = forms.ChoiceField(
        # 这个字段必须要有，不能为空
        # required=True,  # 不为空时改为False就行
        # label="角色",
        choices=(("1", "管理员"), ("2", "客户")),
        # 可写正则表达式
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "name": "role"
            }
        ))

    # 调用form的模板生成html
    email = forms.CharField(
        # 这个字段必须要有，不能为空
        # required=True,
        # label="邮箱",
        validators=[RegexValidator(r"^([a-zA-Z]|[0-9])(\w|\-)+@[a-zA-Z0-9]+\.([a-zA-Z]{2,4})$", '邮箱格式错误')],
        widget=forms.TextInput(
            # 不需要写lable的原因是页面上用的是固定的写法，没有用循环生成

            attrs={"class": "form-control",
                   "placeholder": "输入邮箱",
                   "name": "email"
                   },
        ))

    code = forms.CharField(
        # 这个字段必须要有，不能为空
        # 内部默认就不能为空
        # required=True,
        # label字段，能。出来
        # label="邮箱验证码",
        validators=[RegexValidator(r'^[0-9]{4}$', '验证码是数字')],
        widget=forms.TextInput(
            attrs={"class": "form-control",
                   "placeholder": "输入验证码",
                   "name": "code"
                   }
        )
    )

    # 验证过程写在code钩子里面，能拿到email
    def clean_code(self):
        # 邮箱验证,用户提交的数据
        # 邮箱如果上一个字段校验不通过就获取不到，所以要用get去拿
        email = self.cleaned_data.get("email")
        code = self.cleaned_data["code"]
        if not code:
            # 返回空后校验并不会通过，应该是返回真正的code
            return code

        # 拿去缓存的数据，进行校验
        conn = get_redis_connection("default")
        cache_code = conn.get(email)

        # 缓存不存在
        if not cache_code:
            raise ValidationError("验证码无效")

        # redis拿出来是字节
        if code != cache_code.decode("utf-8"):
            raise ValidationError("验证失败")
        # 正常返回
        return code


# 专门为校验邮箱写的字段
class EmailForm(forms.Form):
    role = forms.ChoiceField(
        # 这个字段必须要有，不能为空
        # required=True,  # 不为空时改为False就行
        # label="角色",
        choices=(("1", "管理员"), ("2", "客户")),
        # 可写正则表达式
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "name": "role"
            }
        ))

    email = forms.CharField(
        label="邮箱地址",
        required=True,
        validators=[RegexValidator(r"^([a-zA-Z]|[0-9])(\w|\-)+@[a-zA-Z0-9]+\.([a-zA-Z]{2,4})$", '邮箱格式错误')])

    # 写email的钩子方法时，能调用到role，因为role字段写在email前面，有先后顺序的
    # 如果前面校验不通过，就拿不到前面的值

    def clean_email(self):

        # 如果没有获取到前面的值，就是前面的值校验失败，直接返回
        role_ = self.cleaned_data["role"]
        email_ = self.cleaned_data["email"]
        if not role_:
            return email_

        # 前面校验成功就去数据库查有没有
        if role_ == "1":
            # 进入管理员表查询，需要查询状态是否唯一
            exist = models.Administrator.objects.filter(active=1, email=email_).exists()
            # print(1)
        else:
            exist = models.Customer.objects.filter(active=1, email=email_).first()

        if not exist:
            # 抛出异常
            raise ValidationError("邮箱不存在")

        code = random.randint(1000, 9999)
        is_send = send_email(email_, code)

        if not is_send[0]:
            raise ValidationError(is_send[1])

        conn = get_redis_connection("default")
        # 设置值和验证码,ex超时时间60s
        conn.set(email_, code, ex=120)
        return email_
