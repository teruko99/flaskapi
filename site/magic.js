let uri = "http://127.0.0.1:5000"
//uri = "http://192.168.0.6:8000"
function desabilita(botao){
    document.getElementById(botao).disabled = true;
    setTimeout(function () {
        document.getElementById(botao).disabled = false;
    }, 3000);
}
function fazGet(url) {
    let request = new XMLHttpRequest()
    request.open("GET", url, false)
    request.send()
    return request.responseText
}
function fazPost(url, body) {
    console.log("Body=", body)
    let request = new XMLHttpRequest()
    request.open("POST", url, true)
    request.setRequestHeader("Content-type", "application/json")
    request.send(JSON.stringify(body))
    request.onload = function() {
        console.log(this.responseText)
    }
    return request.responseText
}
function tellJoke() {
    let data = fazGet(uri + "/jokes");
    let resposta = JSON.parse(data); 
    document.getElementById("neko").src = resposta.cat;  
    document.getElementById("setup").innerHTML = resposta.jokes[0].setup;  
    document.getElementById("punch").innerHTML = resposta.jokes[0].punchline;
}
function criaUsuario() {
    desabilita("btn3")
    event.preventDefault()
    let url = uri + "/users"
    let usuario1 = document.getElementById("usuario1").value
    let senha1 = document.getElementById("senha1").value
    console.log(usuario1)
    console.log(senha1)
    body = {
        "username": usuario1,
        "password": senha1
    }
    fazPost(url, body)
}
function buscaCep() {
    desabilita("btn4")
    event.preventDefault()
	let cep = document.getElementById("cep").value
    let url = uri + "/endereco/" + cep
    console.log(cep)
    body = {
        "cep": cep
    }
    fazPost(url, body)
}
function trazLogs() {
    desabilita("btn6")
    event.preventDefault()
    let url = uri + "/logs"
    fazGet(url)
}
function fazLogin() {
    desabilita("btn5")
    event.preventDefault()
    let url = uri + "/login"
    let usuario2 = document.getElementById("usuario2").value
    let senha2 = document.getElementById("senha2").value
    console.log(usuario2)
    console.log(senha2)
    body = {
        "username": usuario2,
        "password": senha2
    }
    fazPost(url, body)
}