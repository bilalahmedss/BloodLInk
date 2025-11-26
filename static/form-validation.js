document.addEventListener("DOMContentLoaded", function() {

  const passwordInput = document.getElementById("password");
  const passwordToggle = document.getElementById("password-toggle");
  const confirmPasswordInput = document.getElementById("confirm_password");
  const confirmPasswordToggle = document.getElementById("confirm-password-toggle");
  const passwordFeedback = document.getElementById("password-feedback");
  const passwordMatchFeedback = document.getElementById("password-match-feedback");
  const emailInput = document.getElementById("email");
  const emailFeedback = document.getElementById("email-feedback");
  const contactInput = document.getElementById("contact_number") || document.getElementById("number");
  const contactFeedback = document.getElementById("contact-feedback");
  const minLen = 6;

  // ===== Email Validation Feedback =====
  if (emailInput && emailFeedback) {
    emailInput.addEventListener("input", function() {
      const email = emailInput.value;
      
      if (email.length === 0) {
        emailFeedback.textContent = "";
        emailFeedback.classList.remove("text-red-600", "text-green-600");
      } else if (!email.includes("@")) {
        emailFeedback.textContent = " Email must contain @";
        emailFeedback.classList.remove("text-green-600");
        emailFeedback.classList.add("text-red-600");
      } else if (!email.includes(".")) {
        emailFeedback.textContent = " Missing domain extension (.com, .org, etc.)";
        emailFeedback.classList.remove("text-green-600");
        emailFeedback.classList.add("text-red-600");
      } else if (email.match(/^[^\s@]+@[^\s@]+\.[a-zA-Z]{2,}$/)) {
        emailFeedback.textContent = " Email looks valid";
        emailFeedback.classList.remove("text-red-600");
        emailFeedback.classList.add("text-green-600");
      } else {
        emailFeedback.textContent = " Email format invalid";
        emailFeedback.classList.remove("text-green-600");
        emailFeedback.classList.add("text-red-600");
      }
    });
  }

  // ===== Password Eye Icon - Show on Focus, Hide on Blur =====
  if (passwordInput && passwordToggle) {
    // Show eye on focus
    passwordInput.addEventListener("focus", function() {
      passwordToggle.classList.remove("hidden");
    });

    // Hide eye and reset on blur (only if not clicking the button)
    passwordInput.addEventListener("blur", function() {
      setTimeout(() => {
        passwordToggle.classList.add("hidden");
        passwordInput.setAttribute("type", "password");
      }, 100);
    });

    // Toggle password visibility - don't let it blur the field
    passwordToggle.addEventListener("mousedown", function(e) {
      e.preventDefault();
    });

    passwordToggle.addEventListener("click", function(e) {
      e.preventDefault();
      e.stopPropagation();
      const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
      passwordInput.setAttribute("type", type);
      passwordInput.focus();
    });
  }

  // ===== Confirm Password Eye Icon - Show on Focus, Hide on Blur =====
  if (confirmPasswordInput && confirmPasswordToggle) {
    // Show eye on focus
    confirmPasswordInput.addEventListener("focus", function() {
      confirmPasswordToggle.classList.remove("hidden");
    });

    // Hide eye and reset on blur (only if not clicking the button)
    confirmPasswordInput.addEventListener("blur", function() {
      setTimeout(() => {
        confirmPasswordToggle.classList.add("hidden");
        confirmPasswordInput.setAttribute("type", "password");
      }, 100);
    });

    // Toggle password visibility - don't let it blur the field
    confirmPasswordToggle.addEventListener("mousedown", function(e) {
      e.preventDefault();
    });

    confirmPasswordToggle.addEventListener("click", function(e) {
      e.preventDefault();
      e.stopPropagation();
      const type = confirmPasswordInput.getAttribute("type") === "password" ? "text" : "password";
      confirmPasswordInput.setAttribute("type", type);
      confirmPasswordInput.focus();
    });
  }

  // ===== Password Length Feedback with Red/Green Border =====
  if (passwordInput && passwordFeedback) {
    passwordInput.addEventListener("input", function() {
      const currentLength = passwordInput.value.length;
      
      // Update feedback text
      if (currentLength > 0 && currentLength < minLen) {
        passwordFeedback.textContent = `${currentLength}/${minLen} - at least ${minLen} characters required`;
        passwordFeedback.classList.remove("text-green-600");
        passwordFeedback.classList.add("text-red-600");
        // Add red border
        passwordInput.classList.remove("border-green-500");
        passwordInput.classList.add("border-red-500");
      } else if (currentLength >= minLen) {
        passwordFeedback.textContent = ` ${currentLength} characters`;
        passwordFeedback.classList.remove("text-red-600");
        passwordFeedback.classList.add("text-green-600");
        // Add green border
        passwordInput.classList.remove("border-red-500");
        passwordInput.classList.add("border-green-500");
      } else {
        passwordFeedback.textContent = "";
        passwordInput.classList.remove("border-red-500", "border-green-500");
      }
      
      checkPasswordMatch();
    });
  }

  // ===== Password Match Validation =====
  function checkPasswordMatch() {
    if (!confirmPasswordInput || !passwordMatchFeedback) return;
    
    if (passwordInput && passwordInput.value && confirmPasswordInput.value) {
      if (passwordInput.value === confirmPasswordInput.value) {
        confirmPasswordInput.classList.remove("border-red-500");
        confirmPasswordInput.classList.add("border-green-500");
        passwordMatchFeedback.textContent = " Passwords match";
        passwordMatchFeedback.classList.remove("text-red-600");
        passwordMatchFeedback.classList.add("text-green-600");
      } else {
        confirmPasswordInput.classList.remove("border-green-500");
        confirmPasswordInput.classList.add("border-red-500");
        passwordMatchFeedback.textContent = " Passwords do not match";
        passwordMatchFeedback.classList.remove("text-green-600");
        passwordMatchFeedback.classList.add("text-red-600");
      }
    } else {
      confirmPasswordInput.classList.remove("border-red-500", "border-green-500");
      passwordMatchFeedback.textContent = "";
      passwordMatchFeedback.classList.remove("text-red-600", "text-green-600");
    }
  }

  if (confirmPasswordInput) {
    confirmPasswordInput.addEventListener("input", checkPasswordMatch);
  }

  // ===== Contact Number Validation =====
  function validateContact() {
    if (!contactInput || !contactFeedback) return true;
    const val = contactInput.value.trim();
    // Accept digits only; allow spaces or dashes? we'll require digits strictly for now
    const digitsOnly = val.replace(/\D/g, '');
    if (val.length === 0) {
      contactFeedback.textContent = "";
      contactInput.classList.remove("border-red-500", "border-green-500");
      contactFeedback.classList.remove("text-red-600", "text-green-600");
      return false;
    }
    if (digitsOnly.length !== 11) {
      contactFeedback.textContent = "Contact number must be 11 digits";
      contactFeedback.classList.remove("text-green-600");
      contactFeedback.classList.add("text-red-600");
      contactInput.classList.remove("border-green-500");
      contactInput.classList.add("border-red-500");
      return false;
    }
    // valid
    contactFeedback.textContent = "Contact number looks good";
    contactFeedback.classList.remove("text-red-600");
    contactFeedback.classList.add("text-green-600");
    contactInput.classList.remove("border-red-500");
    contactInput.classList.add("border-green-500");
    return true;
  }

  if (contactInput) {
    contactInput.addEventListener("input", validateContact);
    contactInput.addEventListener("blur", validateContact);
  }

  // ===== Form Submission - Validate on Submit Only =====
  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", function(event) {
      let isValid = true;
      
      // Check password length
      if (passwordInput && passwordInput.value.length < minLen) {
        isValid = false;
        passwordFeedback.textContent = "Password must be at least 6 characters";
        passwordFeedback.classList.add("text-red-600");
        passwordInput.classList.add("border-red-500");
      }
      
      // Check password match
      if (passwordInput && confirmPasswordInput) {
        if (passwordInput.value !== confirmPasswordInput.value) {
          isValid = false;
          confirmPasswordInput.classList.add("border-red-500");
          passwordMatchFeedback.textContent = "✗ Passwords do not match";
          passwordMatchFeedback.classList.add("text-red-600");
        }
      }

      // Check contact number length (donor uses contact_number, recipient uses number)
      if (contactInput) {
        const cval = contactInput.value.trim();
        const digits = cval.replace(/\D/g, '');
        if (digits.length !== 11) {
          isValid = false;
          contactInput.classList.add("border-red-500");
          if (contactFeedback) {
            contactFeedback.textContent = "Contact number must be 11 digits";
            contactFeedback.classList.add("text-red-600");
          }
        }
      }
      
      // Check all other required fields
      for (let field of form.elements) {
        if (field.tagName === "INPUT" || field.tagName === "SELECT") {
          if (field.hasAttribute("required") && !field.value.trim()) {
            isValid = false;
            field.classList.add("border-red-500");
          }
        }
      }
      
      if (!isValid) {
        event.preventDefault();
      }
      // If isValid is true, form will submit naturally
    });
  });
});
