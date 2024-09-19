// character_selection.js

import { showCharacterSuggestions } from "./suggestions.js";

// Arrays to keep track of selected characters
export let selectedUserCharacters = [];
export let selectedOpponentCharacters = [];

// Initialize event listeners
export function initEventListeners() {
  // Any additional event listeners can be initialized here
}

// Add character input to a slot
export function addCharacterInput(slotDiv, isUserDefense) {
  slotDiv.innerHTML = "";

  const input = document.createElement("input");
  input.type = "text";
  input.placeholder = "Enter character";
  input.setAttribute("autocomplete", "off");
  input.oninput = function () {
    showCharacterSuggestions(this, isUserDefense);
  };

  const suggestionsDiv = document.createElement("div");
  suggestionsDiv.classList.add("suggestions");

  slotDiv.appendChild(input);
  slotDiv.appendChild(suggestionsDiv);

  // Focus on the input box
  input.focus();

  // Function to close the input box
  function handleClickOutside(event) {
    if (!slotDiv.contains(event.target)) {
      // Remove the input box
      slotDiv.innerHTML = "";
      // Add back the add button
      const addButton = document.createElement("button");
      addButton.type = "button";
      addButton.classList.add("add-character-button");
      addButton.onclick = function () {
        addCharacterInput(slotDiv, isUserDefense);
      };
      addButton.textContent = "+";
      slotDiv.appendChild(addButton);

      // Remove the event listener
      document.removeEventListener("mousedown", handleClickOutside);
    }
  }

  // Attach event listener to the document
  document.addEventListener("mousedown", handleClickOutside);

  // Attach handleClickOutside to input so it can be accessed in suggestions.js
  input.handleClickOutside = handleClickOutside;
}

// Create team slots
export function createTeamSlots(teamDiv, isUserDefense) {
  const numCharacters = window.mode === "3v3" ? 3 : 5;
  const charactersContainer = document.createElement("div");
  charactersContainer.classList.add("characters-container");

  for (let i = 0; i < numCharacters; i++) {
    const slotDiv = document.createElement("div");
    slotDiv.classList.add("character-slot");

    const addButton = document.createElement("button");
    addButton.type = "button";
    addButton.classList.add("add-character-button");
    addButton.onclick = function () {
      addCharacterInput(slotDiv, isUserDefense);
    };
    addButton.textContent = "+";

    slotDiv.appendChild(addButton);
    charactersContainer.appendChild(slotDiv);
  }

  teamDiv.appendChild(charactersContainer);
}
