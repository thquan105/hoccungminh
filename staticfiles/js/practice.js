document.getElementById('reset_btn').addEventListener('click', function () {
    location.reload();
});
document.getElementById('quiz_form').addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const userAnswers = [];
    const cauHoiIds = [];

    document.getElementById('submit_btn').style.display = 'none';
    document.getElementById('reset_btn').classList.remove('hidden');

    formData.forEach((value, key) => {
        userAnswers.push(value);
        cauHoiIds.push(key);
    });

    fetch('submit-answers/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            cauHoi_ids: cauHoiIds,
            dapAnChon: userAnswers,
        }),
    })
        .then(response => response.json())
        .then(data => {
            const { results, total_correct, total_questions } = data;

            results.forEach(result => {
                const questionBlock = document.querySelector(`div[id="${result.cauHoi_id}"]`).closest('.question_block');
                const resultDiv = document.createElement('div');

                if (result.is_correct) {
                    questionBlock.classList.add('bg-green-100');
                    resultDiv.innerHTML = `
                    <p class="font-semibold text-green-600 mt-4">ĐÚNG!</p>
                    <p><strong>Đáp án đúng:</strong> ${result.correct_answer}</p>
                    <p><strong>Giải thích:</strong> ${result.explanation}</p>
                `;
                } else {
                    questionBlock.classList.add('bg-red-100');
                    resultDiv.innerHTML = `
                    <p class="font-semibold text-red-600 mt-4">SAI!</p>
                    <p><strong>Đáp án đúng:</strong> ${result.correct_answer}</p>
                    <p><strong>Giải thích:</strong> ${result.explanation}</p>
                `;
                }

                questionBlock.appendChild(resultDiv);

                document.querySelectorAll('.question_block').forEach((block) => {
                    block.style.pointerEvents = 'none';
                    block.style.transition = 'none';
                });
            });

            const totalResultDiv = document.getElementById('quiz-result');
            totalResultDiv.innerText = `ĐÚNG: ${total_correct} / ${total_questions} câu!`;
        })
        .catch(error => {
            console.error('Error:', error);
        });

});

document.getElementById('doan_van').addEventListener('dblclick', function (event) {
    const selection = window.getSelection().toString().trim();
    if (selection && selection !== " ") {
        showLoading();

        fetch('/vocab/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ word: selection })
        })
            .then(response => response.json())
            .then(data => {
                hideLoading();
                populatePopup(data);
                showPopup();
            })
            .catch(error => {
                hideLoading();
                console.error('Error:', error);
                alert('Something went wrong!');
            });
    }
});

function populatePopup(data) {
    document.getElementById('popup-word').innerText = data.input;
    document.getElementById('popup-ipa').innerHTML = `<button onclick="speakText('${data.input}')">🔊</button>&nbsp;${data.IPA}`;
    document.getElementById('popup-word-form').innerText = data.word_form;
    document.getElementById('popup-meaning').innerText = data.vietnamese_meaning;
    document.getElementById('popup-synonyms').innerText = data.synonyms.join(', ');

    const examples = data.examples.map(example => `<li>
            ${example}
            <button onclick="speakText('${example.replace(/'/g, "\\'")}')">🔊</button>
        </li>`).join('');
    document.getElementById('popup-examples').innerHTML = examples;

    document.getElementById('popup-paragraph').innerText = data.short_paragraph;
    document.getElementById('popup-paragraph-vn').innerText = data.short_paragraph_Vietnamese;
}