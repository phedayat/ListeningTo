window.addEventListener('DOMContentLoaded', (e) => {
	document.getElementById('test').innerHTML = 'Some new text I added';
});

let button = document.getElementsByName('login')[0];
button.addEventListener('click', (e) => {
	document.getElementById('test').innerHTML = 'Changed the text!';
});