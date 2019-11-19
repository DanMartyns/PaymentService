/*
    Requests to the API
*/


/*        SET COOKIE     */
function setCookie(cname, cvalue, exdays) {
  var d = new Date();
  d.setTime(d.getTime() + (exdays*24*60*60*1000));
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

/*     Check Token     */
function checkToken(token){
    fetch("http://localhost:5000/user/check/"+getCookie('token'))
    .then( response => { return response.text(); })
    .then( result => console.log(result));
}

window.addEventListener('load', function () {
    document.getElementById("login").addEventListener("click", login);
});

/*     LOGIN     */
 function login(e){
        e.preventDefault();
        let data = {
            method: 'POST',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({user_id:  document.getElementsByName('user_id')[0].value, password: document.getElementsByName('pass')[0].value})
        }
        fetch('http://localhost:5000/user/login', data)
        .then(response =>  response.json())
        .then(value => {
            let token = value['message']['auth_token'];
            setCookie('token', token);
            let payment = getCookie('payment')
            let url = "http://localhost:5000/payments/"+payment+"/authorize/request"
            window.location.assign(url);
        })
        .catch(function(err) {
            console.log(err)
        });
}
