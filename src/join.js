var connection = new WebSocket('ws://192.168.1.115:8001');
var id = getQueryVariable("id");

connection.onopen = function () {
	console.log("Connected.");
};

connection.onmessage = function (message) {
	var args = message.data.split(" ");

	if (args[0] == "verifyaccept") {
		var name = document.getElementById("username").value;
		window.location.replace("play.html?id=" + id + "&name=" + name + "\n");
	} else
	
	if (args[0] == "verifydeny") {
		var status = document.getElementById("status");
		status.innerHTML = args.slice(1, args.length).join(" ");
		status.style.color = "red";
		document.getElementById("username").value;
	}
};

function getQueryVariable(variable) {
	var query = window.location.search.substring(1);
	var vars = query.split("&");
	for (var i=0;i<vars.length;i++) {
		var pair = vars[i].split("=");
		if (pair[0] == variable) {
			return pair[1];
		}
	} 
}

function verify() {
	var message = "verify " + id + " " + document.getElementById("username").value;
	connection.send(message);
	return false;
}
