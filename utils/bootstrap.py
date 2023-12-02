class BootstrapForm:
    # 排除统一样式的列表，用自定义样式
    exclude_filed_list = []

    def __init__(self, *args, **kwargs):
        # 原先继承关系的上一层，self是调用的那个对象
        super().__init__(*args, **kwargs)
        # 同理field
        for name, field in self.fields.items():
            # 　排除自定义样式字段
            if name in self.exclude_filed_list:
                continue
            field.widget.attrs['class'] = "form-control"
            field.widget.attrs['placeholder'] = "请输入{}".format(field.label)

            # # 尝试从传递给表单的instance对象中获取数据并设置为字段的初始值
            # if 'instance' in kwargs:
            #     instance = kwargs['instance']
            #     if instance and hasattr(instance, name):
            #         initial_value = getattr(instance, name)
            #         field.initial = initial_value
