// var role为body的id，即role
var role_id = document.body.id;
var chineseName = document.getElementById("chineseName").innerText;
console.log(chineseName);
var current_history_id ;
//随机生成一个current_history_id，10位
current_history_id = Math.random().toString(36).substr(2);
console.log(current_history_id)
var helloWord = document.getElementById("helloWord").innerText;
console.log(helloWord)

const username = localStorage.getItem('username');
// console.log(username)

function single_history_delete(history_id){
    $.ajax({
        url: "/history_edit",
        type: 'post',
        data:{
            "user" : username,
            "history_id": history_id,
            "role": role_id,
        },
        success: function (res){
            //如果history_id等于current_history_id，那么清空对话框
            if (history_id === current_history_id){
                document.getElementById('conv-0').innerHTML = '';
            }
            show_history_list();
            // console.log(res)
    }
})}

function generateHistory(history_id,history_name){
    // console.log("generate_history_id_left:",history_id)
    return `<div class="history">
                <i class="bi bi-trash-fill" onclick="single_history_delete('${history_id}')"><img src="../static/images/icon/trash.svg" alt="删除"> </i>
                <a id= ${history_id} class= history-opts-link>
                <i class="bi bi-chat-right-dots" ><img src="../static/images/icon/chat-right-dots.svg"></i>
                <span class="option-text" onclick= "show_history_content('${history_id}')">${history_name}</span>
                </a>
            </div>`
}

function generateMessage(msg){
    return '<p class="dialog-msg">'+ msg +"</p>"
}

function generateDialog(who, msg){
    //修改sapper图片下的文字，将assistant改为sapper
    let name = who;
    if (who === 'assistant') { // 要增加文本转语音的消息框是assistant的
        name = chineseName;
        let voice_msg = msg.replace(/<br>/g, "")
        voice_msg = voice_msg.replace(/"/g, "”");
        voice_msg = voice_msg.replace(/'/g, "‘");
        voice_msg = voice_msg.replace(/\n/g, '');
        voice_msg = voice_msg.replace(/\t/g, '');

    return `<div class="conversation-dialog dialog-${who}" data-role="${who}">
    <div class="dialog-portrait">
        <img src="/static/images/role/${role_id}.png" class="dialog-portrait-img" alt="">
        <p class="dialog-portrait-name">${name}
        </p>
    </div>
    <div class="dialog-msg-wrapper">
        <p class="dialog-msg">${msg}<button class="dialog-msg-btn btn btn-msg" onclick="text2audio('${voice_msg}')"><img src="/static/images/icon/volume-up.svg" alt=""></button></p>
    </div>
</div>`; // 文字转语音，这部分放到 <p class="dialog-msg">里：
// <button class="dialog-msg-btn btn btn-msg" onclick="text2audio('${voice_msg}')">
               // <img src="/static/images/icon/volume-up.svg" alt="">
                //</button>


    }else {
        return `<div class="conversation-dialog dialog-${who}" data-role="${who}">
    <div class="dialog-msg-wrapper">
        <div class="dialog-msg-container">
            <p class="dialog-msg dialog-user">${msg}</p>
        </div>
    </div>
    <div class="dialog-portrait">
        <img src="/static/images/role/${who}.png" class="dialog-portrait-img" alt="">
        <p class="dialog-portrait-name">${name}</p>
    </div>
</div>`;
    }
}

function text2audio(text) {
    console.log(text);
    const utterance = new SpeechSynthesisUtterance(text);
    if (isChinese(text)){
        utterance.lang = 'zh-CN';
    }
    else{
        utterance.lang = 'en-US';
    }
    console.log(utterance.lang);
    utterance.rate = 1;
    window.speechSynthesis.speak(utterance);
    console.log("播放语音");
}

function isChinese(text) {
    const pattern = /[\u4e00-\u9fa5]/; // Unicode范围：中文字符的起始和结束编码
    return pattern.test(text);
}



function show_loading() {
    let convWrapper = $('.conversation-wrapper');
    convWrapper.append(`<div class="conversation-dialog dialog-sapper" data-role="sapper">
        <div class="dialog-portrait">
            <img src="/static/images/role/${role_id}.png" class="dialog-portrait-img" alt="">
            <p class="dialog-portrait-name">${chineseName}</p>
        </div>
        <div class="dialog-msg-wrapper" style="display: inline-block;">
            <div id="result" class="dialog-msg">请求成功,加载中...</div>
        </div>
    </div>`);
}

function new_chat(){
    current_history_id = Math.random().toString(36).substr(2); // 生成随机的history_id
    // 清空对话框
    document.getElementById('conv-0').innerHTML = '';
    $('.conversation-wrapper').append(`<div class="conversation-dialog dialog-assistant" data-role="assistant">
                        <div class="dialog-portrait">
                            <img src="/static/images/role/${role_id}.png" class="dialog-portrait-img" alt="">
                            <p class="dialog-portrait-name">${chineseName}</p>
                        </div>
                        <div class="dialog-msg-wrapper">
                            <p class="dialog-msg" id="helloWord">${helloWord}</p>
                        </div>
                    </div>`);
    console.log(helloWord);
    // show_history_list();
    // console.log("当前页面的id:",current_history_id);
}

function show_history_content(history_id){
    current_history_id = history_id;
    $.ajax({
        url: "/single_history",
        type: 'post',
        data:{
            "user" : username,
            "history_id": history_id,
            "role": role_id,
        },
        success: function (res){
                document.getElementById('conv-0').innerHTML = '';
            res = JSON.parse(res)
            let history = res.single_history
            let length = history.length
            for (let i = 0; i < length; i++)
            {
                if (history[i].role === "user") {
                  // console.log(history[i].content)
                  $('.conversation-wrapper').append(generateDialog("user", history[i].content));
                }
                else if (history[i].role === "assistant") {
                    // console.log(history[i].content)
                      $('.conversation-wrapper').append(generateDialog("assistant", history[i].content));
                }
            }
            $('.conversation-wrapper').animate({
                scrollTop: $('.conversation-wrapper').prop('scrollHeight')
            }, 500)
        }
})}


function show_history_list(){
    //先清空之前添加的history_list
   document.getElementById('conversation-history').innerHTML = '';
  $.ajax({
    url: '/history_list',
    type: 'post',
    data: {
        "user" : username,
        "role": role_id,

    },
    success: function(data) {
        data = JSON.parse(data)
        if (data["history"] === "NULL")
           {
             //console.log("no history")
             //退出success函数
                return;
           }
        else{
            let history = data["history"];
            // console.log(history);
            for (let i = 0; i < history.length; i++) {
                // console.log(history[i].history_id);
                $('.conversation-opts-container').append(generateHistory(history[i].history_id,history[i].content[0].content));
            }
          }
    },
    error: function() {
      //console.log('请求左侧历史记录列表失败！');
    }
  });
}

function ajax_chat(msg){
            // textareaAutoHeight();
            let speach_text = ''
            let tokens = 0
            // console.log(typeof tokens)
            let new_old = 'old' // 判断对话页面是新建吗，传给后端这个变量，减少后端遍历查找，直接追加到文件中
            $("#msgInput").prop("disabled", true);
            let msgInput = $('#msgInput') //获取输入框
            // console.log(msg)
            let convWrapper = $('.conversation-wrapper') // 消息列表 <div id="conv-0" class="conversation-wrapper">
            // 判断convWrapper下是否有子元素
            if (convWrapper.children().length === 0) {
                new_old = 'new'
            }
            $.ajax({
            url: "/get_tokens",
            type: 'post',
            }).done(function(res) {
                // console.log(res["tokens"])
                // console.log(typeof res["tokens"])
                tokens = res["tokens"]  //全局变量没传出去
                if (res["tokens"] <= 0) {
                    $("#msgInput").prop("disabled", false);
                    convWrapper.children().last().remove();
                    alert("使用次数不足，请充值！");
                }else{
                    console.log(msg)
                    show_loading(); // 显示等待状态
                    var source = new EventSource("/chat/" + role_id + "?query=" + msg + "&history_id=" + current_history_id + "&new_old=" + new_old);
                    var begin_output = false
                    let assistantMsg = document.querySelectorAll('.dialog-msg');
                    let lastDialogMsg = assistantMsg[assistantMsg.length - 1];
                    source.onmessage = function(event) { // 服务器返回的数据event.data = '你好，我能为您做什么？' 或者 '[DONE]'
                        if (begin_output === false) {
                            begin_output = true
                            lastDialogMsg.innerHTML = ""
                        }
                        if (event.data === "[DONE]") {
                            source.close() // gpt回答结束，关闭数据流请求
                            show_history_list(); //更新左侧历史记录列表，因为可能是新建的对话要在左边显示

                            // 语音输出
                            speach_text = speach_text.replace(/<br>/g, "");
                            speach_text = speach_text.replace(/"/g, "“");
                            speach_text = speach_text.replace(/'/g, "‘");
                            speach_text = speach_text.replace(/\n/g, '');
                            speach_text = speach_text.replace(/\t/g, '');
                            lastDialogMsg.innerHTML = lastDialogMsg.innerHTML + '<button class="dialog-msg-btn btn btn-msg" onclick="text2audio(\'' + speach_text + '\')">' +
                                                                                '<img src="/static/images/icon/volume-up.svg" alt="">' +
                                                                                '</button>'

                            // 待用版本：语音输出 SpeakJS
                            // console.log(speach_text);
                            // speach_text = speach_text.replace(/<br>/g, "");
                            //
                            // // 使用 SpeakJS 进行语音转换
                            // var speak = new SpeakTTS();
                            // speak.speakText(speach_text);


                            $("#msgInput").prop("disabled", false);
                        }else{
                            lastDialogMsg.innerHTML = lastDialogMsg.innerHTML + event.data

                            speach_text = speach_text + event.data

                            // convWrapper.animate({ // 消息列表滚动到底部
                            //     scrollTop: convWrapper.prop('scrollHeight')
                            // }, 500)
                        }
                    }
                    source.onerror = function (event) {
                        //console.log(event)
                        source.close()
                    }
                }
            }).fail(function(res) {
                //console.log(res);
                alert("获取tokens失败！服务器错误！");
            });
}

$(document).ready(()=>{
    // *** conversation transmission ***
    // input message
    $("#user-setting").click(function() {
        // 点击后，在整个页面中显示一个模态框
        $("#user-setting-modal").modal("show");
        // 向后端查询用户的tokens
        $.ajax({
            url: "/get_tokens",
            type: 'post',
        }).done(function(res) {
            //console.log(res);
            // 将返回的tokens显示到class为modal-body的div中
            $("#tokens").html(res["tokens"]);
        }).fail(function(res) {
            //console.log(res);
            alert("获取tokens失败！");
        });
    });

    $("#close-modal").click(function() {
        // 点击后，将模态框隐藏
        $("#user-setting-modal").modal("hide");
    });


    $("#show-bill").click(function() {
        $("#user-setting-modal").modal("hide");
        // 点击后，显示账单
        $("#user-bill").modal("show");
        // 向后端查询用户的tokens
        $.ajax({
            url: "/get_bill",
            type: 'post',
        }).done(function(res) {
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


        }).fail(function(res) {
            //console.log(res);
            // alert("获取账单失败！");
        });
    });

    $("#close-bill-modal").click(function() {
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

        recognition.onstart = function() {
          //console.log('开始录音');
          isRecording = true;
          // 找到id为speak_i的元素，往里面添加文本'···'
            document.getElementById('speak_i').innerHTML += '···';
        };
        //console.log(recognition);
        recognition.onresult = function(event) {
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

        recognition.onend = function() {
          //console.log('录音结束');
          isRecording = false;
            // 找到id为speak_i的元素，删除文本'···'
            document.getElementById('speak_i').innerHTML = document.getElementById('speak_i').innerHTML.substring(0, document.getElementById('speak_i').innerHTML.length - 3);
        };

        // 点击按钮开始/停止录音
        startRecordingButton.addEventListener('click', function() {
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
$(document).ready(function() {
    show_history_list();

    // 以下代码是为了实现在输入框按下回车键，就发送消息，shift+enter换行
    const msgInput = document.getElementById("msgInput");

    msgInput.addEventListener("keydown", function(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault(); // 阻止默认的提交行为
            query_conversion(); // 调用提交函数
        }
    });
});

function query_conversion(){
        // * display the input message in the conversation wrapper
        let convWrapper = $('.conversation-wrapper') //获取对话框的父元素
        let msgInput = $('#msgInput') //获取输入框
        const msg = msgInput.val() // 获取输入框的值
        // 如果输入框为空，不发送请求
        if (msg === '') {
            return
        }
        // 将用户输入加入对话列表
        convWrapper.append(generateDialog('user', msgInput.val()))
        // console.log(msg)
        msgInput.val('') // 清空输入框

        convWrapper.animate({ // 对话列表自动滚轮到底部
            scrollTop: convWrapper.prop('scrollHeight')
        }, 500)
        // console.log("ajax /chat的history_id:",current_history_id)
        ajax_chat(msg); // ajax访问服务器，获取回复；ajax_chat包含处理等待状态和显示回复
}

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
function redirectToComment(role_id) {
    var url = '/comment/' + role_id; // 构建带有 role_id 的 URL
    window.location.href = url; // 在当前窗口中跳转到指定 URL
}