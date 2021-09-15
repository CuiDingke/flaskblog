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
});
