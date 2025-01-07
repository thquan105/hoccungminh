let isSpeaking = false;

window.addEventListener('scroll', function () {
    const header = document.getElementById('header');
    const scrollY = window.scrollY || window.pageYOffset;

    if (scrollY > 20) {
        header.classList.add('fixed');
    } else {
        header.classList.remove('fixed');
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const menuButton = document.querySelector('#menuButton');
    const navMenu = document.querySelector('#navMenu');
    const menuIcon = document.querySelector('#menuIcon');
    const closeIcon = document.querySelector('#closeIcon');

    menuButton.addEventListener('click', function () {
        navMenu.classList.toggle('hidden');
        navMenu.classList.toggle('block');

        menuIcon.classList.toggle('hidden');
        closeIcon.classList.toggle('hidden');
    });
});

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function speakText(text) {
    if (isSpeaking) {
        return;
    }
    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = 'en-US';
    speech.rate = 0.8;
    speech.pitch = 1;

    isSpeaking = true;

    speech.onend = () => {
        isSpeaking = false;
    };

    speech.onerror = () => {
        console.error('Lỗi khi speak, vui lòng thử lại!');
        isSpeaking = false;
    };

    window.speechSynthesis.speak(speech);
}