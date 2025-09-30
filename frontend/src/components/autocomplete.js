/**
 * Auto-suggestions for name input
 */

export function setupAutocomplete() {
  const entryInput = document.getElementById("entry");
  if (!entryInput || !Array.isArray(window.names)) {
    return;
  }

  // Create dropdown container
  const dropdown = createDropdownElement();
  entryInput.parentNode.appendChild(dropdown);

  let filteredNames = [];
  let selectedIndex = -1;

  entryInput.addEventListener("input", handleInput);
  entryInput.addEventListener("keydown", handleKeydown);
  entryInput.addEventListener("blur", handleBlur);

  function handleInput(e) {
    const query = e.target.value.toLowerCase().trim();
    
    if (query.length === 0) {
      hideDropdown();
      return;
    }

    // Filter names based on input
    filteredNames = window.names.filter(name =>
      name.toLowerCase().includes(query)
    ).slice(0, 8); // Limit to 8 results

    selectedIndex = -1;
    
    if (filteredNames.length > 0) {
      showDropdown(filteredNames);
    } else {
      hideDropdown();
    }
  }

  function handleKeydown(e) {
    if (!dropdown.classList.contains("show") || filteredNames.length === 0) {
      return;
    }

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        selectedIndex = Math.min(selectedIndex + 1, filteredNames.length - 1);
        updateSelection();
        break;
      
      case "ArrowUp":
        e.preventDefault();
        selectedIndex = Math.max(selectedIndex - 1, -1);
        updateSelection();
        break;
      
      case "Enter":
        e.preventDefault();
        if (selectedIndex >= 0) {
          selectName(filteredNames[selectedIndex]);
        }
        break;
      
      case "Escape":
        hideDropdown();
        break;
    }
  }

  function handleBlur() {
    // Delay hiding to allow click selection
    setTimeout(() => hideDropdown(), 150);
  }

  function createDropdownElement() {
    const dropdown = document.createElement("div");
    dropdown.className = "autocomplete-dropdown absolute z-10 w-full bg-white border border-gray-200 rounded-md shadow-lg mt-1 max-h-48 overflow-y-auto hidden";
    return dropdown;
  }

  function showDropdown(names) {
    dropdown.innerHTML = "";
    dropdown.classList.remove("hidden");
    dropdown.classList.add("show");

    names.forEach((name, index) => {
      const item = document.createElement("div");
      item.className = "px-4 py-2 cursor-pointer hover:bg-gray-100 text-sm";
      item.textContent = name;
      item.addEventListener("click", () => selectName(name));
      dropdown.appendChild(item);
    });
  }

  function hideDropdown() {
    dropdown.classList.add("hidden");
    dropdown.classList.remove("show");
    selectedIndex = -1;
  }

  function updateSelection() {
    const items = dropdown.querySelectorAll("div");
    items.forEach((item, index) => {
      item.classList.toggle("bg-primary-100", index === selectedIndex);
      item.classList.toggle("bg-gray-100", index !== selectedIndex);
    });
  }

  function selectName(name) {
    entryInput.value = name;
    hideDropdown();
    entryInput.focus();
  }
}