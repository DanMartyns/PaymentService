/*
    Requests to the API
*/

/*        SET COOKIE     */
function setCookie(cname, cvalue, exminutes) {
  var d = new Date();
  d.setTime(d.getTime() + (exminutes*60*1000));
  var expires = "expires="+ d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

/*     TEST CONNECTION     */
function connection() {
    fetch("http://192.168.85.208/account/connection")
    .then(r => r.json().then(function(data){ console.log("Status Message :", data.message.status) }) );
}

/*        GET COOKIE     */
function getCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for(var i = 0; i <ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

window.addEventListener('load', function () {
    if (getCookie('token') != '' && getCookie('payment') != ''){
      deleteAllCookies();
    }
    const url = window.location.href
    payment_id = url.split("/")[4]
    setCookie("payment", payment_id, 5)
    if (getCookie('token') == ''){
        window.location.assign('http://192.168.85.208/account/login');
    }
    document.getElementById("authorize").addEventListener("click", authorize);
});

/*     AUTHORIZE     */
function authorize(e){
        e.preventDefault();
        payment = getCookie('payment')
        token = getCookie('token')
        let data = {
            method: 'POST',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
              'Authorization' : token
            }
        }
        fetch('http://192.168.85.208/payments/'+payment+'/authorize/response', data)
        .then(response =>  response.json())
        .then(value => {
               document.getElementById("message0").innerHTML = "Your Payment was authorized.";
               document.getElementById("message1").innerHTML = "You can close the page.";
               document.getElementById("message2").innerHTML = "Thank you!";
        })
        .catch(function(err) {
            console.log(err)
        });
}

/* DELETE ALL COOKIES */
function deleteAllCookies() {
 var c = document.cookie.split("; ");
 for (i in c)
  document.cookie =/^[^=]+/.exec(c[i])[0]+"=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
}