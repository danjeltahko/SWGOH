import { selectedUserCharacters } from "./character_selection.js";
import { addCharacterInput } from "./character_selection.js";
import { collectTeams } from "./form_helpers.js";

// Save prestes to a file
export function savePresets() {
  // Collect the data
  const allyCode = document.getElementById("allyCode").value;
  const minGear = document.getElementById("minGear").value;
  const mode = document.querySelector('input[name="mode"]:checked').value;
  const rank = document.getElementById("rank").value;

  // Collect user's defense teams
  console.log("Collecting user defense teams...");
  const userDefense = collectTeams("userDefenseContainer");

  // Prepare data to save
  const data = {
    allyCode: allyCode,
    minGear: minGear,
    mode: mode,
    rank: rank,
    userDefense: userDefense,
  };

  // Convert data to JSON string
  const dataStr = JSON.stringify(data, null, 2);

  // Create a Blob from the data
  const blob = new Blob([dataStr], { type: "application/json" });

  // Create a link element
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "gac_presets.json";

  // Append to the document and trigger the download
  document.body.appendChild(link);
  link.click();

  // Clean up
  document.body.removeChild(link);
}

// Import presets from a file
export function importPresets(event) {
  console.log("Importing presets...");
  const file = event.target.files[0];
  if (!file) {
    return;
  }

  const reader = new FileReader();
  reader.onload = function (e) {
    try {
      const data = JSON.parse(e.target.result);

      // Populate the settings
      document.getElementById("allyCode").value = data.allyCode || "";
      document.getElementById("minGear").value = data.minGear || 1;
      document.querySelector(
        `input[name="mode"][value="${data.mode || "3v3"}"]`,
      ).checked = true;
      document.getElementById("rank").value = data.rank || "kyber";

      // Update the form to reflect changes
      updateForm();

      // Populate user's defense teams
      populateUserDefense(data.userDefense);

      alert("Presets imported successfully!");
    } catch (error) {
      console.error("Error parsing presets file:", error);
      alert("Failed to import presets. Please ensure the file is valid.");
    }
  };

  reader.readAsText(file);
}

// Populate user's defense teams from file
export function populateUserDefense(userDefenseData) {
  for (const zoneName in userDefenseData) {
    const zoneDiv = document.getElementById(`zone_${zoneName}`);
    if (!zoneDiv) {
      console.warn(`Zone ${zoneName} not found in the DOM.`);
      continue;
    }

    const teams = userDefenseData[zoneName];
    const teamDivs = zoneDiv.querySelectorAll(".team");

    teams.forEach((teamData, index) => {
      const teamDiv = teamDivs[index];
      if (!teamDiv) {
        console.warn(`Team ${index + 1} in zone ${zoneName} not found.`);
        return;
      }

      const characters = teamData.defense;
      const charSlots = teamDiv.querySelectorAll(".character-slot");

      characters.forEach((charData, slotIndex) => {
        const slotDiv = charSlots[slotIndex];
        if (!slotDiv) {
          console.warn(
            `Character slot ${slotIndex + 1} in team ${index + 1} not found.`,
          );
          return;
        }

        // Create the character image element
        const characterDisplay = document.createElement("img");
        characterDisplay.src = charData.image;
        characterDisplay.alt = charData.name;
        characterDisplay.classList.add("character-image");

        // Add a delete button
        const deleteButton = document.createElement("button");
        deleteButton.textContent = "×";
        deleteButton.classList.add("delete-character");
        deleteButton.onclick = function () {
          // Remove character from selected list
          const selectedCharacters = selectedUserCharacters;
          const charName = charData.name;
          const index = selectedCharacters.indexOf(charName);
          if (index > -1) {
            selectedCharacters.splice(index, 1);
          }
          // Reset the slot
          slotDiv.innerHTML = "";
          // Add back the add button
          const addButton = document.createElement("button");
          addButton.type = "button";
          addButton.classList.add("add-character-button");
          addButton.onclick = function () {
            addCharacterInput(slotDiv, true);
          };
          addButton.textContent = "+";
          slotDiv.appendChild(addButton);
        };

        // Clear the slot and add the character image and delete button
        slotDiv.innerHTML = "";
        slotDiv.appendChild(characterDisplay);
        slotDiv.appendChild(deleteButton);

        // Add character to selectedUserCharacters
        if (!selectedUserCharacters.includes(charData.name)) {
          selectedUserCharacters.push(charData.name);
        }
      });
    });
  }
}
