// var role为body的id，即role
var role_id = document.body.id;
var chineseNameElement = document.getElementById("chineseName");
var chineseName = document.getElementById("chineseName").innerText;
console.log(chineseName);
var userName = document.getElementById("userName").innerText;


$(document).ready(() => {
    // *** conversation transmission ***
    // input message
    $("#user-setting").click(function () {
        // 点击后，在整个页面中显示一个模态框
        $("#user-setting-modal").modal("show");
        // 向后端查询用户的tokens
        $.ajax({
            url: "/get_tokens",
            type: 'post',
        }).done(function (res) {
            //console.log(res);
            // 将返回的tokens显示到class为modal-body的div中
            $("#tokens").html(res["tokens"]);
        }).fail(function (res) {
            //console.log(res);
            alert("获取tokens失败！");
        });
    });

    $("#close-modal").click(function () {
        // 点击后，将模态框隐藏
        $("#user-setting-modal").modal("hide");
    });


    $("#show-bill").click(function () {
        $("#user-setting-modal").modal("hide");
        // 点击后，显示账单
        $("#user-bill").modal("show");
        // 向后端查询用户的tokens
        $.ajax({
            url: "/get_bill",
            type: 'post',
        }).done(function (res) {
            // 后端 return {'2023-06-22': {'wanneng': 2, 'xingzuo': 1}}
            //console.log(res);
            // 取出返回的字典
            let bill = res["bill"];
            //console.log(bill);
            // 构建表格 HTML
            let tableHtml = "<table class='bill-table'>";
            tableHtml += "<tr><th>日期</th><th>角色</th><th>使用次数</th></tr>";

            // 遍历字典中的数据并添加到表格中
            for (let date in bill) {

                // 获取物品及数量的子字典
                let items = bill[date];
                for (let item in items) {
                    tableHtml += "<tr class='one-day'>";
                    // 添加日期
                    tableHtml += "<td>" + date + "</td>";
                    // 添加物品名称和数量
                    tableHtml += "<td>" + item + "</td>";
                    tableHtml += "<td>" + items[item] + "</td>";
                    // 换行
                    tableHtml += "</tr>";
                }
// 添加空行
                tableHtml += "<td colspan='3'></td></tr>";

            }

            tableHtml += "</table>";
            // 将表格 HTML 添加到指定的 div 中
            $("#bill").html(tableHtml);


        }).fail(function (res) {
            //console.log(res);
            // alert("获取账单失败！");
        });
    });

    $("#close-bill-modal").click(function () {
        // 点击后，将模态框隐藏
        $("#user-bill").modal("hide");
    });


    /**
     * 判断字符的语言类型
     * @param {string} text 待判断的文本
     * @returns {string} 语言类型（en: 英文, zh: 中文）
     */
    function getCharacterLang(text) {
        const zhRegExp = new RegExp('[\\u4E00-\\u9FA5]+'); // 匹配中文字符的正则表达式
        const enRegExp = new RegExp('[a-zA-Z]+'); // 匹配英文字符的正则表达式

        if (zhRegExp.test(text)) {
            return 'zh';
        } else if (enRegExp.test(text)) {
            return 'en';
        } else {
            return '';
        }
    }


    // 语音输入
    const startRecordingButton = document.getElementById('startRecording');
    const msgInput = document.getElementById('msgInput');
    let recognition = null;
    let isRecording = false;

    // 初始化语音识别对象
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        //console.log('webkitSpeechRecognition');
    } else if ('SpeechRecognition' in window) {
        recognition = new SpeechRecognition();
        //console.log('SpeechRecognition');
    }

    if (recognition) {
        recognition.continuous = true;
        // recognition.interimResults = true;

        recognition.onstart = function () {
            //console.log('开始录音');
            isRecording = true;
            // 找到id为speak_i的元素，往里面添加文本'···'
            document.getElementById('speak_i').innerHTML += '···';
        };
        //console.log(recognition);
        recognition.onresult = function (event) {
            const result = event.results[event.results.length - 1];
            const transcript = result[0].transcript;

            //console.log('识别结果:', transcript);
            // 判断识别结果中字符的类型
            const lang = getCharacterLang(transcript);

            // 设置语言
            if (lang === 'en') {
                // recognition.lang = 'en-US'; // 英文
                recognition.lang = 'zh-CN'; // 中文
            } else if (lang === 'zh') {
                recognition.lang = 'zh-CN'; // 中文
            } else {
                console.log('识别结果:', recognition.lang);
                recognition.lang = 'zh-CN'; // 中文
                // recognition.lang = 'en-US'; // 默认为英文
            }
            console.log('识别结果:', recognition.lang);
            // 在结果末尾添加标点符号
            const finalTranscript = transcript + ' '; // 这里使用句号作为标点符号，可以根据需要修改

            // 追加到输入框
            msgInput.value += finalTranscript;
        };

        recognition.onend = function () {
            //console.log('录音结束');
            isRecording = false;
            // 找到id为speak_i的元素，删除文本'···'
            document.getElementById('speak_i').innerHTML = document.getElementById('speak_i').innerHTML.substring(0, document.getElementById('speak_i').innerHTML.length - 3);
        };

        // 点击按钮开始/停止录音
        startRecordingButton.addEventListener('click', function () {
            if (isRecording) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });
    } else {
        console.error('浏览器不支持Web Speech API');
    }
})

//进入页面或新建页面，访问服务器，获取历史记录，显示在左边
$(document).ready(function () {

    // 以下代码是为了实现在输入框按下回车键，就发送消息，shift+enter换行
    const msgInput = document.getElementById("msgInput");

    msgInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault(); // 阻止默认的提交行为
            query_conversion_comment(); // 调用提交函数
        }
    });
});

function searchBill() {
    var input = document.getElementById('searchInput').value; // 获取搜索框中的输入值
    var rows = document.querySelectorAll('.bill-table tbody tr'); // 获取所有账单行

    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        var cells = row.getElementsByTagName('td'); // 获取该行的所有单元格

        var matchFound = false; // 是否找到匹配项
        for (var j = 0; j < cells.length; j++) {
            var cellContent = cells[j].innerText; // 获取单元格的文本内容

            if (cellContent.includes(input)) { // 判断单元格内容是否包含搜索关键字
                matchFound = true;
                break;
            }
        }

        if (matchFound) {
            row.style.display = 'table-row'; // 显示匹配的行
        } else {
            row.style.display = 'none'; // 隐藏未匹配的行
        }
    }
}


/*new add*/
function CommentToChat(role_id) {
    var url = '/select/' + role_id; // 构建带有 role_id 的 URL
    window.location.href = url; // 在当前窗口中跳转到指定 URL
}

function generateCommentSelf(who, msg,likes=0) {
    return `<div class="conversation-dialog dialog-user" data-role="user">
                    <div class="dialog-msg-wrapper">
                        <div class="dialog-msg-container">
                            <p class="dialog-msg dialog-user">${msg}</p>
                        </div>
                    </div>
                    <div class="dialog-portrait">
                        <img src="/static/images/role/user.png" class="dialog-portrait-img" alt="">
                        <p class="dialog-portrait-name">${who}</p>
                    </div>
                    <div class="icon-container">
                        <i class="delete-icon" onclick="toggleDelete('${msg}',${who})"><img class="delete-icon" src="../static/images/icon/trash.svg" alt="删除图标"></i>
                        <div>
                            <i class="like-icon">
                                <img class="like-img" src="../static/images/icon/heart-outline.svg" alt="点赞图标" data-liked="false" data-count="${likes}" onclick="toggleLike(this,${who},'${msg}')">
                                <span class="like-count">${likes}</span>
                            </i>
                        </div>
                    </div>
                </div>`;
}

function generateComment(who, msg,likes) {
    return `<div class="conversation-dialog dialog-assistant" data-role="assistant">
                    <div class="dialog-portrait">
                        <img src="/static/images/role/user.png" class="dialog-portrait-img" alt="">
                        <p class="dialog-portrait-name">${who}
                        </p>
                    </div>
                    <div class="dialog-msg-wrapper" style="height: 100px">
                        <p class="dialog-msg">${msg}</p>
                    </div>
                    <div class="icon-container">
                        <div>
                            <i class="like-icon">
                                <img class="like-img" src="../static/images/icon/heart-outline.svg" alt="点赞图标" data-liked="false" data-count="${likes}" onclick="toggleLike(this,${who},'${msg}')">
                                <span class="like-count">${likes}</span>
                            </i>
                        </div>
                    </div>
                </div>`;
}

function noComment() {
    return `<div class="conversation-dialog dialog-assistant" data-role="assistant">
                    <div class="dialog-portrait">
                        <img src="/static/images/role/user.png" class="dialog-portrait-img" alt="">
                        <p class="dialog-portrait-name">noBody
                        </p>
                    </div>
                    <div class="dialog-msg-wrapper">
                        <p class="dialog-msg">暂无评论，快来抢沙发吧！</p>
                    </div>
                </div>`;
}

function query_conversion_comment() {
    let convWrapper = $('.conversation-wrapper') //获取对话框的父元素
    let msgInput = $('#msgInput') //获取输入框
    const msg = msgInput.val() // 获取输入框的值
    console.log(convWrapper.attr('id'));
    // 如果输入框为空，不发送请求
    if (msg === '') {
        return
    }
    // 如果对话列表仅有一条暂无评论的提示，删除该提示
    if (convWrapper.data('specialValue') === 'noComment') {
        //清空对话列表
        convWrapper.empty();
        // 将特殊值设为空
        convWrapper.data('specialValue', '');
    }
    console.log(convWrapper);
    // 将用户输入加入对话列表
    convWrapper.append(generateCommentSelf(userName, msgInput.val()))
    var source =new EventSource("/chatComment/" + role_id + "?comments=" + msgInput.val());
    // 监听事件源的error事件，处理连接错误或关闭事件源的情况
    source.onerror = function(event) {
        console.error('EventSource failed:', event);
        source.close(); // 关闭事件源
    };
    msgInput.val('') // 清空输入框
    convWrapper.animate({ // 对话列表自动滚轮到底部
        scrollTop: convWrapper.prop('scrollHeight')
    }, 500)
}

function toggleLike(likeImg,who,msg) {
    // 获取点赞图标内的 img 元素
    const imgElement = likeImg;
    //获得被点赞的角色
    const role = who;
    //获得被点赞的内容
    const comment = msg;
    console.log(role);
    console.log(comment);

    // 获取当前点赞状态和点赞数量
    const isLiked = imgElement.getAttribute('data-liked') === 'true';
    let likeCount = parseInt(imgElement.getAttribute('data-count'));

    // 定义要替换的图片路径
    const heartOutlineSrc = '../static/images/icon/heart-outline.svg';
    const heartSolidSrc = '../static/images/icon/heart-solid.svg';

    // 根据当前点赞状态进行切换
    if (isLiked) {
        imgElement.src = heartOutlineSrc + '?t=' + Date.now(); // 添加随机参数
        imgElement.setAttribute('data-liked', 'false');
        likeCount--;
    } else {
        imgElement.src = heartSolidSrc + '?t=' + Date.now(); // 添加随机参数
        imgElement.setAttribute('data-liked', 'true');
        likeCount++;
    }

    // 更新点赞数量显示
    const likeCountElement = imgElement.parentNode.querySelector('.like-count');
    likeCountElement.textContent = likeCount;

    // 更新点赞数量记录
    imgElement.setAttribute('data-count', likeCount.toString());

    // 向后端发送点赞请求
    var source = new EventSource("/comment_edit/" + role_id + "?likes=" + likeCount+"&who="+role+"&comment="+comment);

    // 监听事件源的error事件，处理连接错误或关闭事件源的情况
    source.onerror = function(event) {
        console.error('EventSource failed:', event);
        source.close(); // 关闭事件源
    };

    // 在点赞请求发送成功后，关闭事件源
    source.onopen = function(event) {
        source.close(); // 关闭事件源
    };
}

function toggleDelete(msg,who) {
    //获得被删除的角色
    const role = who;
    //获得被删除的内容
    const comment = msg;

    // 向后端发送删除请求
    var source = new EventSource("/comment_delete/" + role_id + "?who="+role+"&comment="+comment);

    // 监听事件源的error事件，处理连接错误或关闭事件源的情况
    source.onerror = function(event) {
        console.error('EventSource failed:', event);
        source.close(); // 关闭事件源
    };

    // 在删除请求发送成功后，关闭事件源
    source.onopen = function(event) {
        source.close(); // 关闭事件源
    };
    //提示删除成功
    alert("删除成功！");
    //刷新页面
    window.location.reload();
}