document.addEventListener('DOMContentLoaded', () => {
  const predictionForm = document.getElementById('predictionForm');
  const messageDiv = document.getElementById('message');

  predictionForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const phoneNumber = document.getElementById('phoneNumber').value;
    const otp = document.getElementById('otp').value;
    const prediction = document.getElementById('prediction').value;

    try {
      const response = await fetch('/prediction', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ phoneNumber, otp, prediction }),
      });

      const data = await response.json();

      if (response.ok) {
        messageDiv.textContent = data.message;
        messageDiv.style.color = 'green';
        predictionForm.reset();
      } else {
        messageDiv.textContent = data.error;
        messageDiv.style.color = 'red';
      }
    } catch (error) {
      console.error('Error:', error);
      messageDiv.textContent = 'An error occurred. Please try again.';
      messageDiv.style.color = 'red';
    }
  });
});
