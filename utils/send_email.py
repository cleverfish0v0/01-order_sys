import smtplib
from email.mime.text import MIMEText


def send_email(receiver_email, code):
    try:
        # todo：邮箱真实性验证？？？
        # todo:同一邮箱60秒内不用重复发送
        # 查询缓存中是否存在该邮箱，如果有则抛出错误，没有就能继续发
        # 同一ip一分钟内不用发太多次

        # 发件人邮箱和SMTP授权码
        sender_email = "3078184064@qq.com"
        sender_password = "aidhnvbyywrddcff"

        # 收件人邮箱
        receiver_email = receiver_email

        # 邮件内容
        subject = "验证码"
        content = "这是你的验证码: {}".format(code)  # 你可以将验证码替换成你想要发送的内容

        # 创建邮件
        message = MIMEText(content, "plain", "utf-8")
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject

        # 连接SMTP服务器
        smtp_server = "smtp.qq.com"
        smtp_port = 587

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # 开启TLS加密
        server.login(sender_email, sender_password)

        # 发送邮件
        server.sendmail(sender_email, [receiver_email], message.as_string())

        # 关闭连接
        server.quit()

        # 邮件发送成功
        return (True, "邮件发送成功")

    except smtplib.SMTPException as e:
        # 邮件发送失败
        print("邮件发送失败: " + str(e))
        return (False, "邮件发送失败 ")
    except Exception as e:
        # 其他异常
        print("其他异常: " + str(e))
        return (False, "其他异常")


if __name__ == "__main__":
    is_send = send_email("qqd@qq.com", 8867)
    print(is_send)
