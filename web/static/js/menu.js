//绑定事件,加载完后执行
    $(function () {
        $(".multi-menu .title").click(function () {
            //toggleClass的作用是，有这个类就去掉，没这个类就加上
            $(this).next().toggleClass('hide')
        })
    })