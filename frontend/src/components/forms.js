/**
 * Form handling
 */

export function setupForms() {
  setupAreaForm();
  setupSigninForm();
}

function setupAreaForm() {
  const form = document.getElementById("area-form");
  if (!form) return;

  const select = document.getElementById("area-select");
  const errorElement = document.getElementById("area-error");

  form.addEventListener("submit", (event) => {
    const isValid = select && select.value;

    if (!isValid) {
      event.preventDefault();
      showError(errorElement, "Please select an area");
      select?.focus();
    } else {
      hideError(errorElement);
    }
  });

  // Clear error on selection change
  select?.addEventListener("change", () => {
    hideError(errorElement);
  });
}

function setupSigninForm() {
  const form = document.getElementById("signin-form");
  if (!form) return;

  const entryInput = document.getElementById("entry");
  const errorElement = document.getElementById("input-error");
  let clickedButton = null;

  // Track which button was clicked
  const buttons = form.querySelectorAll("button[type='submit']");
  buttons.forEach((btn) => {
    btn.addEventListener("click", (event) => {
      clickedButton = event.target;
    });
  });

  form.addEventListener("submit", (event) => {
    const name = entryInput?.value?.trim();

    if (!name) {
      event.preventDefault();
      showError(errorElement, "Please enter a name");
      entryInput?.focus();
      return;
    }

    // Validate name exists in the list
    if (window.names && !window.names.includes(name)) {
      event.preventDefault();
      showError(
        errorElement,
        "Name not found. Please select from the suggestions."
      );
      entryInput?.focus();
      return;
    }

    hideError(errorElement);

    // Add loading state to buttons
    if (clickedButton) {
      clickedButton.disabled = true;
      clickedButton.classList.add("opacity-50");
      const originalText = clickedButton.textContent;
      clickedButton.textContent = "Processing...";

      // Reset after 3 seconds (fallback)
      setTimeout(() => {
        clickedButton.disabled = false;
        clickedButton.classList.remove("opacity-50");
        clickedButton.textContent = originalText;
      }, 3000);
    }
  });
}

function showError(errorElement, message) {
  if (!errorElement) return;

  errorElement.textContent = message;
  errorElement.classList.remove("hidden");
  errorElement.classList.add("animate-fade-in");
}

function hideError(errorElement) {
  if (!errorElement) return;

  errorElement.classList.add("hidden");
  errorElement.classList.remove("animate-fade-in");
}
