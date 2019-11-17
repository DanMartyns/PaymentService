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

window.addEventListener('load', function () {

    if( getCookie('token') == "" ){
        const url = window.location.href
        payment_id = url.split("/")[4]
        setCookie("payment", payment_id, 1)
        location.replace("http://localhost:5000/account/login");
    }
    else {
        document.getElementById("authorize").addEventListener("click", authorize);
    }

});

/*     PRINT TRANSACTIONS
function repeatTransactionDiv(transactionName){
    return '<div class="col-md-4 col-sm-6"> \
        <div class="service-block"> \
            <div class="pull-left bounce-in"> \
                <i class="fa fa-money fa fa-md"></i> \
            </div> \
            <div class="media-body fade-up"> \
                <h3 class="media-heading">'+transactionName+'</h3> \
                <p>Nay middleton him admitting consulted and behaviour son household. Recurred advanced he oh together entrance speedily suitable. Ready tried gay state fat could boy its among shall.</p> \
            </div> \
        </div> \
    </div>'
}

async function loadInfo(){
    try{
        const rawResponse = await fetch('http://localhost:5000/payments', {
            method: 'POST',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({user_id:  document.getElementsByName('user_id')[0].value, password: document.getElementsByName('pass')[0].value})
        });
        const content = await rawResponse.json();

        var container = document.getElementById('services')

        for (var i = 0; i < 3; i++){
            container.innerHTML += repeatTransactionDiv('Bilhete de ida')
        }
        for (var i = 0; i < 3; i++){
            container.innerHTML += repeatTransactionDiv('Bilhete de volta')
        }
    } catch(error){
        logMyErrors(error);
    }
}
*/
/*     AUTHORIZE     */
async function authorize(){
    try{
        const payment = getCookie('payment')
        const rawResponse = await fetch('http://localhost:5000/payments/'+payment+'/authorize/response', { //TODO: change payment_id
            method: 'POST',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
              'Authorization' : payment
            },
        });
        const content = await rawResponse.json();
        console.log(content); //TODO: return successPage.html, telling the payment was successful authorized
    } catch(error){
        logMyErrors(error);
    }
}