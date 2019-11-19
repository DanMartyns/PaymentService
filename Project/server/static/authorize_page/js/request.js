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
    //console.log(getCookie('payment'))
    //const url = window.location.href
    //payment_id = url.split("/")[4]
    //setCookie("payment", payment_id, 1)
    document.getElementById("authorize").addEventListener("click", authorize);
});

/*     Check Token
function checkToken(token){
    fetch("http://localhost:5000/user/check/"+getCookie('token'))
    .then( response => { return response.text(); })
    .then( result => console.log(result));
}
*/
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
        fetch('http://localhost:5000/payments/'+payment+'/authorize/response', data)
        .then(response =>  response.json())
        .then(value => {
            console.log(value)
        })
        .catch(function(err) {
            console.log(err)
        });
}