
$(function () {
    bindDeleteEvent();
    bindConfirmDeleteEvent();
});

function bindDeleteEvent() {
    $(".btn-delete").click(
        function () {
            $('#deleteModal').modal('show')
            DELETE_ID = $(this).attr('cid');
            console.log(DELETE_ID)
        }
    )
}

function bindConfirmDeleteEvent() {
            $('#btnconfirmDelete').click(function () {
                console.log("确认删除", DELETE_ID)
                //清空内部
                $('.deleteError').empty();
                //$('#deleteModal').modal('hide')
                //发送ajax请求,/xxx/xxx/?数据
                $.ajax({
                    url: DELETE_URL,
                    type: 'GET',
                    data: {'cid': DELETE_ID},
                    dataType: 'JSON',
                    success: function (res) {
                        if (res.status) {
                            console.log(res);
                            //删除后更改页面的两种方法
                            //方式一：删除成功重定向
                            location.reload(res.url);
                            //方式二：找到当前行删除掉,字符串相加DELETE_ID
                            // $("tr[row-id='2']").remove()
                        } else {
                            //失败处理，展示页面信息
                            $('.deleteError').text(res.detail);
                        }

                    }
                })
            })
        }