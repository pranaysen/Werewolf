var ip = "";
var httpport = "";
var wsport = "";
var connection;

function getConf() {
	return jQuery.getJSON("conf.json")
		.then(function (json) {
			return {
				ip: json.ip,
				httpport: json.httpport,
				wsport: json.wsport
			}
		})
};

getConf().then(function(returndata){
	ip = returndata.ip;
	httpport = returndata.httpport;
	wsport = returndata.wsport;
	
	console.log("ws://" + returndata.ip + ":" + returndata.wsport);
	
	connection = new WebSocket(("ws://" + ip + ":" + wsport));
	connection.onopen = function () {
		console.log("Connected.");
	};

	connection.onmessage = function (message) {
		var args = message.data.split(" ");
		console.log(args);

		if (args[0] == "createaccept") {
			var status = document.getElementById("status");
			var url = ip + ":" + httpport + "/join.html?id=" + args[1];
			status.innerHTML = "Game created! Url: " + url;
			status.style.color = "green";
		} else

		if (args[0] == "createdeny") {
			var status = document.getElementById("status");
			status.innerHTML = "An unkown error has occurred";
			status.style.color = "red";
		}
	};
});

function updateTotal() {
	var villager = document.getElementById("villager").value;
	var werewolf = document.getElementById("werewolf").value;
	var doctor = document.getElementById("doctor").value;
	var seer = document.getElementById("seer").value;
	var monkey = document.getElementById("monkey").value;
	var total = parseInt(villager) + parseInt(werewolf) + parseInt(doctor) + parseInt(seer) + parseInt(monkey);
	var totalDoc = document.getElementById("total");
	totalDoc.value = total;
	return false;
}

function createGame() {
	var gameParameters = "creategame ";
	gameParameters += document.getElementById("villager").value;
	gameParameters += " ";
	gameParameters += document.getElementById("monkey").value;
	gameParameters += " ";
	gameParameters += document.getElementById("seer").value;
	gameParameters += " ";
	gameParameters += document.getElementById("werewolf").value;
	gameParameters += " ";
	gameParameters += document.getElementById("doctor").value;
	gameParameters += " ";
	gameParameters += document.getElementById("total").value;
	gameParameters += "\n";
	connection.send(gameParameters);

	var status = document.getElementById("status");
	return false;
}