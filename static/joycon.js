var hasGP = false;
var repGP;
var pressed = [false, false, false, false, false, false, false, false, false, false, false, false]
var stick_active = [false, false]
/* joycon mapping
html id - abstract id - switch   - mapping
1       - 0           - a        - a
2       - 1           - y        - b
4       - 2           - l        - l
5       - 3           - r        - r
6       - 4           - zl       - y
7       - 5           - zr       - x
10      - 6           - ra click - select
11      - 7           - la click - start
12      - d_0         - d-up     - d-up
13      - d_1         - d-down   - d-down
14      - d_2         - d-left   - d-left
15      - d_3         - d-right  - d-right
*/ 
var skip = 0;
var frameskip = document.currentScript.getAttribute('frameskip'); // this will make the game run at only ~15 (4) or ~ 20 (3) FPS
var joystick_timeout = 0;

var fps = 30;

var sending = false;

function update(){
	reportOnGamepad();

	if (skip == frameskip){ // skip some frames 
		updateImage();				
		skip = 0;
	}
	else{
		skip++;
	}
	window.requestAnimationFrame(update);
}

function updateImage() {
	document.getElementById("image").src="static/img.jpg?t=" + new Date().getTime(); // reload updated image without caching
}

function sendJoystick(ax0, ax1, id) { // sends joystick information back to the flask app (server.py) using XML post requests
				  // since the Switch browser does not support WebSocket
	if (!(sending)){
		var req = new XMLHttpRequest();
		req.open('POST', '/', true);
		req.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
                if (id == 0){
			req.send("key=" +"Stick;"+"1"+";"+ax0+";"+ax1);
			}
		else {
			req.send("key=" +"Stick;"+"2"+";"+ax0+";"+ax1);
			}
		sending = false;
	}
}

function sendKey(key){
	if (!(sending)){
		var req = new XMLHttpRequest();
		req.open('POST', '/', true);
		req.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
		req.send("key=" + key);
		sending = false;
	}
}

function getJoystick() {
	var gp = navigator.getGamepads()[0];
	if(joystick_timeout == 2){ //limit joystick data so it doesn't induce more lag
		joystick_timeout = 0;        
		for(var i=0;i<4; i+=2) {
			if (((gp.axes[i] > 0.1) || (gp.axes[i] < -0.1)) || ((gp.axes[i+1] > 0.1) || (gp.axes[i+1] < -0.1))) {
				sendJoystick(gp.axes[i], gp.axes[i+1], i);
                                stick_active[i] = true;
			}
                        else {
				if (stick_active[i] == true){
					sendKey("s"+i/2+"_up");
                                	stick_active[i] = false;}
                        
			}
		}
	}
	else{joystick_timeout++;}
}

function reportOnGamepad() {
	var gp = navigator.getGamepads()[0];
	
	for(var i=0;i<gp.buttons.length;i++) {			
		if(gp.buttons[i].pressed){		
			switch (i){
				case 1:
					if (!pressed[0]){
					sendKey("0_down");
					pressed[0] = true;};
					break;
				case 2:
					if (!pressed[1]){
					sendKey("1_down");
					pressed[1] = true;};
					break;
				case 4:
					if (!pressed[2]){
					sendKey("2_down");
					pressed[2] = true;};
					break;
				case 5:
					if (!pressed[3]){
					sendKey("3_down");
					pressed[3] = true;};
					break;
				case 6:
					if (!pressed[4]){
                                        sendKey("4_down");									
					pressed[4] = true;};
					break;
				case 7:
					if (!pressed[5]){
					sendKey("5_down");
					pressed[5] = true;};
					break;
				case 10:
					if (!pressed[6]){
					sendKey("6_down");
					pressed[6] = true;};
					break;
				case 11:
					if (!pressed[7]){
					sendKey("7_down");
					pressed[7] = true;};
					break;
				case 12:
					if (!pressed[8]){
					sendKey("d0_down");
					pressed[8] = true;};
					break;
				case 13:
					if (!pressed[9]){
					sendKey("d1_down");
					pressed[9] = true;};
					break;
				case 14:
					if (!pressed[10]){
					sendKey("d2_down");
					pressed[10] = true;};
					break;
				case 15:
					if (!pressed[11]){						
					sendKey("d3_down");
					pressed[11] = true;};
					break;

			}
		} else if(!(gp.buttons[i].pressed)){
			switch (i){
				case 1:
					if (pressed[0]){
					sendKey("0_up");
					pressed[0] = false;};
					break;
				case 2:
					if (pressed[1]){
					sendKey("1_up");
					pressed[1] = false;};
					break;
				case 4:
					if (pressed[2]){
					sendKey("2_up");
					pressed[2] = false;};
					break;
				case 5:
					if (pressed[3]){
					sendKey("3_up");
					pressed[3] = false;};
					break;
				case 6:
					if (pressed[4]){
					sendKey("4_up");
					pressed[4] = false;};
					break;
				case 7:
					if (pressed[5]){
					sendKey("5_up");
					pressed[5] = false;};
					break;
				case 10:
					if (pressed[6]){
					sendKey("6_up");
					pressed[6] = false;};
					break;
				case 11:
					if (pressed[7]){
					sendKey("7_up");
					pressed[7] = false;};
					break;
				case 12:
					if (pressed[8]){
					sendKey("d0_up");
					pressed[8] = false;};
					break;
				case 13:
					if (pressed[9]){
					sendKey("d1_up");
					pressed[9] = false;};
					break;
				case 14:
					if (pressed[10]){
					sendKey("d2_up");
					pressed[10] = false;};
					break;
				case 15:
					if (pressed[11]){
					sendKey("d3_up");
					pressed[11] = false;};
					break;



			}
		}
	}

	getJoystick();
}
