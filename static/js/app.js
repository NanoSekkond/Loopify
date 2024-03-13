function checkForQueryAndCookies() {
    window.onbeforeunload = stopLoop;
    const urlParams = new URLSearchParams(window.location.search);
    let code = urlParams.get('code');
    if (code != null) {
        setCookie("code", code);
        window.location.href = window.location.href.split("?")[0];
    }
    else {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/run_get_token', true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4 && xhr.status == 200) {
                response = JSON.parse(xhr.response);
                setCookie("access_token", response[0], 3600);
                setCookie("refresh_token", response[1]);
                deleteCookie("code");
                deleteCookie("code_verifier");
            }
            if (xhr.readyState == 4 && xhr.status == 400) {
                document.getElementById("login_button").disabled = false;
                document.getElementById("login_button").textContent = "Login";
                document.getElementById("log_out_text").innerHTML = ""
            }
            if (getCookie("access_token") != null) {
                document.getElementById("login_button").disabled = true;
                document.getElementById("log_out_text").innerHTML = '<p>Not you? Click <a onclick="deleteCookies()">here</a> to log out.</p>'
                var xhr_name = new XMLHttpRequest();
                xhr_name.open('GET', '/run_get_user', true);
                xhr_name.onreadystatechange = function() {
                    document.getElementById("login_button").textContent = "Logged as " + xhr_name.responseText;
                }
                xhr_name.send();
            }
        };
        xhr.send();
    }
}

function login() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/run_login', true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            response = JSON.parse(xhr.response);
            setCookie("code_verifier", response[1]);
            window.location.href = response[0];
        }
    };
    xhr.send();
}

function startLoop() {
    var start = document.getElementById("start-input").value;
    var end = document.getElementById("end-input").value;
    var data = new FormData();
    data.append("start", start);
    data.append("end", end);
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/start_loop', true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 400) {
            alert(xhr.responseText);
            document.getElementById("start_loop_button").disabled = false;
            document.getElementById("start_loop_button").textContent = "Start Loopify"
            document.getElementById("stop_loop_button").disabled = true;
        }
    };
    xhr.send(data);
    document.getElementById("start_loop_button").disabled = true;
    document.getElementById("start_loop_button").textContent = "Looping..."
    document.getElementById("stop_loop_button").disabled = false;
}

function stopLoop() {
    var xhr = new XMLHttpRequest();
    xhr.open('PUT', '/stop_loop', true);
    xhr.send();
    document.getElementById("start_loop_button").disabled = false;
    document.getElementById("start_loop_button").textContent = "Start Loopify"
    document.getElementById("stop_loop_button").disabled = true;
}

function deleteCookies() {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i];
        const eqPos = cookie.indexOf("=");
        const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
        deleteCookie(name);
    }
    stopLoop();
    checkForQueryAndCookies();
}

function setCookie(name, value, seconds) {
    var expires = "";
    if (seconds) {
        var date = new Date();
        date.setTime(date.getTime() + (seconds*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}

function deleteCookie(name) {
    document.cookie = name +'=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop().split(';').shift();
    }
    else {
        return null;
    }
}