function send_code() {
        // 阻止表单默认提交
        $("#registerForm").submit(function(e) {
            e.preventDefault();
        });
        // 获取id="register-username"和id="register-password"的input标签的值
        var phone = $("#register-username").val();

        // 判断phone是否为11位
        if (phone.length !== 11) {
            alert("请输入11位手机号！");
            // 启用表单默认提交
            $("#registerForm").unbind("submit");
            return;
        }
        var is_phone = true;

        var password = $("#register-password").val();
        // 判断密码是否为空，为空则提示用户输入密码，终止函数
        if (password === "") {
            alert("请输入密码！");
            // 启用表单默认提交
            $("#registerForm").unbind("submit");
            return;
        }
        var have_password = true;
        var code = $("#code").val();
        var button = document.getElementById("verification-code");
        button.disabled = true; // 禁用按钮防止重复点击
        // 启用表单默认提交
        $("#registerForm").unbind("submit");
        // 如果flag_phone和flag_password都为true，则发送ajax请求
        if ( is_phone && have_password) {
            $.ajax({
            url: "/register",
            type: "get",
            data: {
                "phone": phone,
            },
            success: function(code_msg) {
                //code_msg = {"code":406,"msg":"手机格式不正确，格式为11位的数字.","smsid":"0"}
                code_msg = JSON.parse(code_msg);
                // 解析服务器返回的json数据
                if (code_msg.code === 2) {
                    alert("发送成功！");
                } else {
                    alert(code_msg.msg);
                    // 终止send_code函数
                    return;
                }
            }
        });}
        button.innerText = "60秒倒计时";

        localStorage.setItem('seconds', 60);
        var now = new Date().getTime();
        var expire = now + 60 * 1000;
        localStorage.setItem('expire', expire);
            var seconds = localStorage.getItem('seconds');
        var countdown = setInterval(function() {
            seconds--;
            button.innerText = seconds + "秒倒计时";

            if (seconds <= 0) {
                clearInterval(countdown);
                button.innerText = "发送验证码";
                button.disabled = false; // 启用按钮
            }
        }, 1000);
    }


document.addEventListener("DOMContentLoaded", function() {
    var username = $("#login-username").val();
    // 存为全局变量给chat.js使用
    // window.username = username; // chat.js中的username = window.username;
    localStorage.setItem('username', username);
    //console.log(username);
    var button = document.getElementById("verification-code");
    button.addEventListener("click", send_code);
});