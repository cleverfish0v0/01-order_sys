// 用于csrf设置，重复使用
//从游览器页面获取请求
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

//判断是否为需要添加csrftoken的请求方式
//这些请求不携带
function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

//在这里提前设置ajax请求的csrftoken设置
$.ajaxSetup({
    //xhr是xml，http的request对象
    //发起请求之前提前加载，发送之前执行
    beforeSend: function (xhr, settings) {
        //判定，只有需要csrf的请求时才添加csrftoken
        //只要是ajax请求就给他带上csrftokn（在请求头）
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader('X-CSRFToken', getCookie("csrftoken"));
        }
    }
})
