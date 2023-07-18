// You can add any JavaScript functionality here if needed
const registrationForm = document.getElementById('registrationForm');
const ageCheckbox = document.getElementById('ageCheckbox');
const parentForm = document.getElementById('parentForm');

ageCheckbox.addEventListener('change', function() {
  if (this.checked) {
    parentForm.classList.add('hidden');
  } else {
    parentForm.classList.remove('hidden');
  }
});

registrationForm.addEventListener('submit', function(e) {
  e.preventDefault();

  // Get form field values
  const firstName = document.getElementById('firstName').value;
  const lastName = document.getElementById('lastName').value;
  const email = document.getElementById('email').value;
  const phone = document.getElementById('phone').value;

  // Validate form data
  if (ageCheckbox.checked || (parentForm.classList.contains('hidden') && firstName && lastName && email && phone)) {
    // Successful registration, redirect to success page or dashboard
    window.location.href = 'success.html';
  } else {
    // Invalid form data, display error message
    alert('Please fill in all required fields and confirm your age.');
  }
});
