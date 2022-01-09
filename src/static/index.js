window.addEventListener('DOMContentLoaded', (e) => {
	document.getElementById('test').innerHTML = 'Some new text I added';
});

let button = document.getElementsByName('login');
button.addEventListener('click', (e) => {
	document.getElementById('test').innerHTML = 'Changed the text!';
});