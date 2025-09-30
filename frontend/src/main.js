import "./styles/main.scss";
import { setupAutocomplete } from "./components/autocomplete";
import { setupFlashMessages } from "./components/flash-messages";
import { setupForms } from "./components/forms";

class App {
  constructor() {
    this.init();
  }

  async init() {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => this.setup());
    } else {
      this.setup();
    }
  }

  setup() {
    setupForms();
    setupAutocomplete();
    setupFlashMessages();

    this.setupFocus();
  }

  setupFocus() {
    const entryInput = document.getElementById("entry");
    if (entryInput) {
      // Autofocus and select on load
      setTimeout(() => {
        entryInput.focus();
        entryInput.select();
      }, 100);
    }
  }
}

// Init app
new App();
