/*
    Requests to the API
*/


/*        SET COOKIE     */
function setCookie(cname, cvalue, exseconds) {
  var d = new Date();
  d.setTime(d.getTime() + (exseconds*1000));
  var expires = "expires="+ d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
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
/*     TEST CONNECTION     */
function connection() {
    fetch("http://192.168.85.208/account/connection")
    .then(r => r.json().then(function(data){ console.log("Status Message :", data.message.status) }) );
}

window.addEventListener('load', function () {
    document.getElementById("login").addEventListener("click", login);
});

/*     LOGIN     */
 function login(e){
        e.preventDefault();
        if ( (document.getElementsByName('user_id')[0].value).length > 0 && (document.getElementsByName('pass')[0].value).length > 0 ){
            let data = {
                method: 'POST',
                headers: {
                  'Accept': 'application/json',
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({user_id:  document.getElementsByName('user_id')[0].value, password: document.getElementsByName('pass')[0].value})
            }
            fetch('http://192.168.85.208/user/login', data)
            .then(response =>  response.json())
            .then(value => {
                let token = value['message']['auth_token'];
                setCookie('token', token, 5);
                let payment = getCookie('payment')
                let url = "http://192.168.85.208/payments/"+payment+"/authorize/request"
                document.location.replace(url);
            })
            .catch(function(err) {
                console.log(err)
            });
        }

}