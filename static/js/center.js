$(function () {
    // 显示  隐藏 登陆方式  先隐藏 后展示
    $(".logintab").hide();
    $(".logintab").first().show();
    $("#tab span").each(function (i) {
        $(this).click(function () {
            $(".logintab").hide();
            $(".logintab").eq(i).show();
        })
    });

    tinymce.init({
        selector: '.mytextarea',
        height: 400,
        plugins: "quickbars emoticons",
        inline: false,
        toolbar: true,
        menubar: true,
        quickbars_selection_toolbar: 'bold italic | link h2 h3 blockquote',
        quickbars_insert_toorbar: 'quickimage quicktable',
    })
    $('#inputPhone').blur(function () {
        let phone = $(this).val();
        let span_ele = $(this).next('span');
        if (phone.length == 11) {
            span_ele.text('');
            // {#jqery ajax  get请求#}
            $.get('/user/checkphone', {phone: phone}, function (data) {
                    // {#console.log(data)#}
                    if (data.code != 200) {
                        span_ele.css({"color": "#ff0011", "font-size": "12px"});
                        span_ele.text(data.msg);
                    }
                }
            )
        } else {
            span_ele.css({"color": "#ff0011", "font-size": "12px"});
            span_ele.text('手机格式错误');
        }
    });

    // 相册图片的删除
    $('.photo-del').click(function () {
        flag = confirm('确定删除此图片？')
        if (flag) {
            // 获取属性值tag tag属性就是图片的主键
            let pid = $(this).attr('tag');
            console.log(pid)
            // 1.ajax 2.location.href
            location.href = '/user/photo_del?pid=' + pid;
        }


    });
});
