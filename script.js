document.addEventListener("DOMContentLoaded", () => {
    const startQuizButton = document.getElementById('start-quiz');
    const submitAnswerButton = document.getElementById('submit-answer');
    const questionText = document.getElementById('question-text');
    const optionsContainer = document.getElementById('options');

    if (startQuizButton) {
        startQuizButton.addEventListener('click', () => {
            // Start the quiz with a sample category
            fetchQuizQuestions('science');
        });
    }

    if (submitAnswerButton) {
        submitAnswerButton.addEventListener('click', () => {
            const selectedAnswer = document.querySelector('input[name="option"]:checked');
            if (selectedAnswer) {
                submitAnswer(selectedAnswer.value);
            } else {
                alert('Please select an answer.');
            }
        });
    }
});

function fetchQuizQuestions(category) {
    // Make an AJAX request to start the quiz
    fetch(`/start_quiz/${category}`)
        .then(response => response.json())
        .then(data => {
            displayQuestion(data.question);
        })
        .catch(error => console.error('Error fetching quiz questions:', error));
}

function displayQuestion(question) {
    questionText.textContent = question.text;
    optionsContainer.innerHTML = '';

    for (const [key, value] of Object.entries(question.options)) {
        const optionLabel = document.createElement('label');
        optionLabel.innerHTML = `<input type="radio" name="option" value="${key}">${key}: ${value}`;
        optionsContainer.appendChild(optionLabel);
        optionsContainer.appendChild(document.createElement('br'));
    }
}

function submitAnswer(answer) {
    // Handle answer submission
    fetch('/submit_answer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ answer })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.feedback);
        // Optionally fetch the next question here
    })
    .catch(error => console.error('Error submitting answer:', error));
}

