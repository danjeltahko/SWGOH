// suggestions.js

import { addCharacterInput } from "./character_selection.js";
import {
  selectedUserCharacters,
  selectedOpponentCharacters,
} from "./character_selection.js";

export let characterData = [];

// Fetch character data
export function initCharacterData() {
  return fetch("/static/data/all_characters.json")
    .then((response) => response.json())
    .then((data) => {
      characterData = data;
      window.characterData = data; // Expose to global scope if needed
    })
    .catch((error) => {
      console.error("Error loading character data:", error);
    });
}

// Show character suggestions
export function showCharacterSuggestions(inputElement, isUserDefense) {
  const value = inputElement.value.toLowerCase();
  const suggestionsContainer = inputElement.nextElementSibling;
  suggestionsContainer.innerHTML = "";

  if (value.length === 0 || characterData.length === 0) {
    return;
  }

  // Determine which selected characters list to use
  const selectedCharacters = isUserDefense
    ? selectedUserCharacters
    : selectedOpponentCharacters;

  // Get characters already selected in the same team
  const teamDiv = inputElement.closest(".team");
  const selectedCharsInTeam = [];
  const charSlots = teamDiv.querySelectorAll(".character-slot");
  charSlots.forEach((slot) => {
    if (slot !== inputElement.parentElement) {
      const img = slot.querySelector(".character-image");
      if (img) {
        selectedCharsInTeam.push(img.alt);
      }
    }
  });

  const combinedSelectedCharacters =
    selectedCharacters.concat(selectedCharsInTeam);

  const matchedCharacters = characterData.filter(
    (char) =>
      char.name.toLowerCase().includes(value) &&
      !combinedSelectedCharacters.includes(char.name),
  );

  matchedCharacters.forEach((char) => {
    const suggestionItem = document.createElement("div");
    suggestionItem.classList.add("suggestion-item");

    const img = document.createElement("img");
    img.src = char.image;
    img.alt = char.name;

    const nameSpan = document.createElement("span");
    nameSpan.textContent = char.name;

    suggestionItem.appendChild(img);
    suggestionItem.appendChild(nameSpan);

    // Prevent the document's mousedown handler from firing when clicking on a suggestion
    suggestionItem.addEventListener("mousedown", function (event) {
      event.stopPropagation();
    });

    suggestionItem.addEventListener("click", function () {
      const selectedCharName = char.name;
      const selectedCharImage = char.image;
      inputElement.value = selectedCharName;
      suggestionsContainer.innerHTML = "";

      // Replace the input with the character image
      const characterDisplay = document.createElement("img");
      characterDisplay.src = selectedCharImage;
      characterDisplay.alt = selectedCharName;
      characterDisplay.classList.add("character-image");

      // Add a delete button
      const deleteButton = document.createElement("button");
      deleteButton.textContent = "×";
      deleteButton.classList.add("delete-character");
      deleteButton.onclick = function () {
        // Remove character from selected list
        const index = selectedCharacters.indexOf(selectedCharName);
        if (index > -1) {
          selectedCharacters.splice(index, 1);
        }
        // Reset the slot
        const slotDiv = characterDisplay.parentElement;
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
      };

      const slotDiv = inputElement.parentElement;
      slotDiv.innerHTML = "";
      slotDiv.appendChild(characterDisplay);
      slotDiv.appendChild(deleteButton);

      // Add character to selected list
      selectedCharacters.push(selectedCharName);

      // Remove the event listener since the input is removed
      if (inputElement.handleClickOutside) {
        document.removeEventListener(
          "mousedown",
          inputElement.handleClickOutside,
        );
        inputElement.handleClickOutside = null;
      }
    });

    suggestionsContainer.appendChild(suggestionItem);
  });
}

// Close suggestions when clicking outside
document.addEventListener("click", function (event) {
  const suggestions = document.querySelectorAll(".suggestions");
  suggestions.forEach((suggestion) => {
    if (!suggestion.contains(event.target)) {
      suggestion.innerHTML = "";
    }
  });
});
