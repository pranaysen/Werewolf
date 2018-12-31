var name = getQueryVariable("name");
var id = getQueryVariable("id");
var player_id;
var connection = new WebSocket('ws://192.168.1.115:8001');
var chatEnabled = 1;

document.getElementById("buttonmasterdiv").style.display = "none";

connection.onopen = function() {
	console.log("Connected.");
	var message = "join ";
	message += id;
	message += " ";
	message += name;
	connection.send(message);
};

connection.onmessage = function (message) {
	console.log(message.data);
	parseMessage(message.data);
};

document.getElementById("groupid")
	.addEventListener("keyup", function(event) {
	event.preventDefault();
	console.log("owo");
	if (event.keyCode === 13) {
		document.getElementById("send").click();
	}
});

function parseMessage(message) {
	var args = message.split(" ");

	switch (args[0]) {
		case "gamechat":
			displayGameMessage(args);
			break;
		case "timer":
			startTimer(args);
			break;
		case "kill":
			document.getElementById("groupid").disabled = true;
			break;
		case "revive":
			document.getElementById("groupid").disabled = false;
			break;
		case "enablechat":
			document.getElementById("groupid").disabled = false;
			break;
		case "disablechat":
			document.getElementById("groupid").disabled = true;
			break;
		case "chat":
			displayChatMessage(args);
			break;
		case "joinaccept":
			player_id = args[1];
			break;
		case "status":
			setStatus(args);
			break;
		case "gamestate":
			setGameState(args);
			break;
		case "showbuttons":
			showButtons(args);
			break;
		case "hidebuttons":
			hideButtons(args);
			break;
		case "gamewhisper":
			displayGameWhipser(args);
			break;
	}
}

function hideButtons(args) {
	document.getElementById("buttonmasterdiv").style.display = "none";
	var buttondiv = document.getElementById("buttondiv");
	while (buttondiv.firstChild) {
		buttondiv.removeChild(buttondiv.firstChild);
	}
}

function setGameState(args) {
	document.getElementById("gamestate").innerHTML = args.slice(1, args.length).join(" ");

	var textarea = document.getElementById('textbox');
	textarea.scrollTop = textarea.scrollHeight;
}

function setStatus(args) {
	status = args.slice(2, args.length).join(" ");
	document.getElementById("status").innerHTML = status;
	document.getElementById("status").style.color = args[1];
}

function displayGameMessage(args) {
	var output = "Game: ";
	output += args.slice(1, args.length).join(" ");

	var box = document.getElementById("textbox");
	box.innerHTML += "\n" + output;
}

function displayGameWhipser(args) {
	var output = "Game (to you): ";
	output += args.slice(1, args.length).join(" ");

	var box = document.getElementById("textbox");
	box.innerHTML += "\n" + output;
}

function startTimer(args) {
	var time = parseInt(args[1])
	var message = args.slice(2, args.length).join(" ");

	var timerId = setInterval(countdown, 1000);

	function countdown() {
		var timer = document.getElementById("status");
		if (time == -1) {
			timer.innerHTML = "";
			clearTimeout(timerId);
		} else {
			timer.innerHTML = time + " " + message;
			time--;
		}
	}
}

function displayChatMessage(args) {
	var output = args.slice(1, args.length).join(" ");

	var box = document.getElementById("textbox");
	box.innerHTML += "\n" + output;

	var textarea = document.getElementById('textbox');
	textarea.scrollTop = textarea.scrollHeight;
}

function getQueryVariable(variable) {
	var query = window.location.search.substring(1);
	var vars = query.split("&");
	for (var i = 0; i < vars.length; i++) {
		var pair = vars[i].split("=");
		if (pair[0] == variable) {
			return pair[1];
		}
	}
}

function updateTextbox() {
	if (chatEnabled == 1) {
		// chat
		console.log("what");
		var text = document.getElementById("groupid");
		var box = document.getElementById("textbox");
		box.innerHTML += "\n" + name + ": " + text.value;

		var connectionMsg = "chat " + id + " " + player_id + " " + text.value;
		connection.send(connectionMsg);

		text.value = "";

		var textarea = document.getElementById('textbox');
		textarea.scrollTop = textarea.scrollHeight;
	}
	
	return false;
}

function showButtons(args) {
	console.log(args[1]);
	nameA = args[1].replace(/;/g, " ")
	data = args[2].split(";");
	renderButtons(nameA, data);
}

function renderButtons(nameA, data) {
	document.getElementById("buttonstate").innerHTML = nameA;
	var buttons = document.getElementById("buttondiv");

	for (var i = 0; i < data.length; i++) {
		var button = document.createElement("button");
		button.setAttribute("name", data[i]);
		button.innerHTML = data[i];

		button.addEventListener("click", function(event) {
			var btn = event.target;
			var btnid = btn.getAttribute("name");
			connection.send("buttonclick " + id + " " + player_id + " " + btnid);

			document.getElementById("buttonmasterdiv").style.display = "none";
			var buttondiv = document.getElementById("buttondiv");
			while (buttondiv.firstChild) {
				buttondiv.removeChild(buttondiv.firstChild);
			}
		});

		buttons.appendChild(button);
	}
	
	document.getElementById("buttonmasterdiv").style.display = "block";
}