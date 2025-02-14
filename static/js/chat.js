const chatHistory = document.getElementById('chat-history');
const userInput = document.getElementById('user-input');
const cuocTroChuyenId = document.getElementById('cuocTroChuyen_id').value;
const form = document.getElementById('chat-form');

window.onload = function () {
    chatHistory.scrollTop = chatHistory.scrollHeight;
};

function getFormattedTime() {
    const currentDate = new Date();
    const hours = currentDate.getHours();
    const minutes = currentDate.getMinutes();
    const seconds = currentDate.getSeconds();
    const formattedTime = `${hours}:${minutes < 10 ? '0' + minutes : minutes}:${seconds < 10 ? '0' + seconds : seconds}`;

    return formattedTime;
}

async function sendMessage() {
    // Lấy và làm sạch tin nhắn từ input
    const userMessage = userInput.value.trim();
    if (!userMessage) return;

    userInput.value = '';

    // Tạo và thêm tin nhắn của người dùng vào giao diện chat
    const userMessageWrapper = document.createElement('div');
    userMessageWrapper.classList.add('flex', 'items-start', 'justify-end', 'space-x-2', 'animate-fade-in');

    const userMessageElement = document.createElement('div');
    userMessageElement.classList.add('bg-indigo-600', 'rounded-lg', 'p-3', 'max-w-[70%]');
    userMessageElement.innerHTML = `<p class="text-white break-words">${userMessage}</p><span class="text-xs text-indigo-200 mt-1 block">${getFormattedTime()}</span>`;

    const userAvatar = document.createElement('img');
    userAvatar.classList.add('w-8', 'h-8', 'rounded-full');
    userAvatar.src = userAvatarUrl;
    userAvatar.alt = 'User';

    userMessageWrapper.appendChild(userMessageElement);
    userMessageWrapper.appendChild(userAvatar);
    chatHistory.appendChild(userMessageWrapper);

    chatHistory.scrollTop = chatHistory.scrollHeight;

    try {
        // Gửi yêu cầu đến server
        const response = await fetch('response/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                userInput: userMessage,
                cuocTroChuyen_id: cuocTroChuyenId
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();

        const botMessage = data.response;

        // Tạo và thêm tin nhắn từ bot vào giao diện chat
        const botMessageWrapper = document.createElement('div');
        botMessageWrapper.classList.add('flex', 'items-start', 'space-x-2', 'animate-fade-in');

        const botAvatar = document.createElement('img');
        botAvatar.classList.add('w-8', 'h-8', 'rounded-full');
        botAvatar.src = botAvatarUrl;
        botAvatar.alt = 'AI';

        const botMessageElement = document.createElement('div');
        botMessageElement.classList.add('bg-gray-100', 'rounded-lg', 'p-3', 'max-w-[70%]');
        botMessageElement.innerHTML = `<p class="text-gray-800 break-words">${botMessage}</p><span class="text-xs text-gray-500 mt-1 block">${getFormattedTime()}</span>`;

        botMessageWrapper.appendChild(botAvatar);
        botMessageWrapper.appendChild(botMessageElement);
        chatHistory.appendChild(botMessageWrapper);

        chatHistory.scrollTop = chatHistory.scrollHeight;

    } catch (error) {
        console.error('Error:', error);

        // Hiển thị thông báo lỗi trong giao diện chat
        botMessageWrapper = document.createElement('div');
        botMessageWrapper.classList.add('flex', 'items-start', 'space-x-2', 'animate-fade-in');

        botAvatar = document.createElement('img');
        botAvatar.classList.add('w-8', 'h-8', 'rounded-full');
        botAvatar.src = '{% static "images/icon/ico-bot.png" %}';
        botAvatar.alt = 'AI';

        botMessageElement = document.createElement('div');
        botMessageElement.classList.add('bg-gray-100', 'rounded-lg', 'p-3', 'max-w-[70%]');
        botMessageElement.innerHTML = `<p class="text-gray-800">Có lỗi xảy ra. Vui lòng thử lại sau.</p><span class="text-xs text-gray-500 mt-1 block">${getFormattedTime()}</span>`;

        botMessageWrapper.appendChild(botAvatar);
        botMessageWrapper.appendChild(botMessageElement);
        chatHistory.appendChild(botMessageWrapper);

        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
}

userInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();       
        form.dispatchEvent(new Event('submit'));
    } else if (event.key === 'Enter' && event.shiftKey) {
        event.preventDefault();
        const cursorPosition = userInput.selectionStart;
        userInput.value =
            userInput.value.slice(0, cursorPosition) + '\n' + userInput.value.slice(cursorPosition);
        userInput.selectionStart = userInput.selectionEnd = cursorPosition + 1;
    }
});

let isSubmitting = false;

form.addEventListener('submit', (event) => {
    event.preventDefault();
    const loader = document.getElementById('loader');
    const submitButton = form.querySelector('button[type="submit"]');
    const defaultSvg = submitButton.querySelector('#defaultSvg');
    const loadingSvg = submitButton.querySelector('#loadingSvg');

    if (isSubmitting) return;
    isSubmitting = true;

    defaultSvg.classList.add('hidden');
    loadingSvg.classList.remove('hidden');

    submitButton.disabled = true;
    loader.style.display = 'block';
    sendMessage().finally(() => {
        submitButton.disabled = false;
        isSubmitting = false;
        loader.style.display = 'none';
        defaultSvg.classList.remove('hidden');
        loadingSvg.classList.add('hidden');
    });
});