/**
 * Message Popups
 */

export function setupFlashMessages() {
  const flashMessages = document.querySelectorAll("[data-flash-message]");
  
  flashMessages.forEach(setupFlashMessage);
}

function setupFlashMessage(message) {
  // Auto-dismiss after 5 seconds
  const autoDismissTimer = setTimeout(() => {
    dismissMessage(message);
  }, 5000);

  // Manual dismiss on click
  message.addEventListener("click", () => {
    clearTimeout(autoDismissTimer);
    dismissMessage(message);
  });

  // Add dismiss button
  const dismissBtn = document.createElement("button");
  dismissBtn.innerHTML = `
    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
    </svg>
  `;
  dismissBtn.className = "ml-auto text-current opacity-70 hover:opacity-100 transition-opacity";
  dismissBtn.setAttribute("aria-label", "Dismiss message");
  dismissBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    clearTimeout(autoDismissTimer);
    dismissMessage(message);
  });

  message.appendChild(dismissBtn);
}

function dismissMessage(message) {
  message.style.transform = "translateX(100%)";
  message.style.opacity = "0";
  
  setTimeout(() => {
    message.remove();
  }, 300);
}

/**
 * Show a new flash message programmatically
 */
export function showFlashMessage(text, type = "info") {
  const container = document.getElementById("flash-container") || createFlashContainer();
  
  const message = document.createElement("div");
  message.setAttribute("data-flash-message", "");
  message.className = getFlashMessageClasses(type);
  message.innerHTML = `
    <span>${text}</span>
  `;

  container.appendChild(message);
  setupFlashMessage(message);

  // Animate in
  requestAnimationFrame(() => {
    message.style.transform = "translateX(0)";
    message.style.opacity = "1";
  });
}

function createFlashContainer() {
  const container = document.createElement("div");
  container.id = "flash-container";
  container.className = "fixed top-4 right-4 z-50 space-y-2";
  document.body.appendChild(container);
  return container;
}

function getFlashMessageClasses(type) {
  const baseClasses = "flex items-center p-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full opacity-0 max-w-md";
  
  const typeClasses = {
    success: "bg-success-50 text-success-800 border border-success-200",
    error: "bg-error-50 text-error-800 border border-error-200", 
    warning: "bg-warning-50 text-warning-800 border border-warning-200",
    info: "bg-primary-50 text-primary-800 border border-primary-200"
  };

  return `${baseClasses} ${typeClasses[type] || typeClasses.info}`;
}