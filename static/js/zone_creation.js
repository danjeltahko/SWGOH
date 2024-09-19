// zone_creation.js

import { createTeamSlots } from "./character_selection.js";

import { selectedUserCharacters } from "./character_selection.js";

// Create a zone (used for both user's defense and opponent's defense)
export function createZone(zoneName, numTeams, isUserDefense) {
  // Create zone div
  const zoneDiv = document.createElement("div");
  zoneDiv.classList.add("zone");
  // Create zone header depending on the type of zone
  const zoneHeader = document.createElement(isUserDefense ? "h4" : "h3");
  zoneHeader.textContent = `Zone ${zoneName}`;
  zoneDiv.appendChild(zoneHeader);

  let contentDiv; // Declare contentDiv here to access it later

  // Assign unique IDs
  if (isUserDefense) {
    // Assign unique ID for user's defense
    zoneDiv.id = `user_zone_${zoneName}`;
    // Create collapsible zone header
    const arrowSpan = document.createElement("span");
    arrowSpan.classList.add("collapse-arrow");
    arrowSpan.textContent = "▼"; // Down arrow
    // Append arrow to zone header
    zoneHeader.appendChild(arrowSpan);
    zoneHeader.classList.add("collapsible");
    // Create zone content div
    contentDiv = document.createElement("div");
    contentDiv.classList.add("zone-content");
    // Append zone content to zone div
    zoneDiv.appendChild(contentDiv);
    // Append zone content to zone div
    zoneHeader.onclick = function () {
      contentDiv.classList.toggle("collapsed");
      // Toggle arrow direction
      if (contentDiv.classList.contains("collapsed")) {
        arrowSpan.textContent = "►"; // Right arrow
      } else {
        arrowSpan.textContent = "▼"; // Down arrow
      }
    };
  } else {
    // Assign unique ID for opponent's defense
    zoneDiv.id = `opponent_zone_${zoneName}`;
  }

  for (let i = 1; i <= numTeams; i++) {
    // Create team div
    const teamDiv = document.createElement("div");
    teamDiv.classList.add("team");

    // Assign a unique identifier
    // teamDiv.dataset.zoneName = zoneName;
    // teamDiv.dataset.teamIndex = i; // Use i or a unique team ID if available

    // Create team wrapper
    const teamWrapper = document.createElement("div");
    teamWrapper.classList.add("team-wrapper");
    // Create team header
    const teamHeader = document.createElement("div");
    teamHeader.classList.add("team-header");
    // Add team label
    const label = document.createElement("label");
    label.textContent = `Team ${i}:`;
    teamHeader.appendChild(label);

    // For opponent's defense, add eliminated checkbox
    if (!isUserDefense) {
      const statusToggle = document.createElement("div");
      statusToggle.classList.add("status-toggle");

      const toggleInput = document.createElement("input");
      toggleInput.type = "checkbox";
      toggleInput.id = `eliminated_${zoneName}_${i}`;
      toggleInput.classList.add("eliminated-checkbox");

      const toggleLabel = document.createElement("label");
      toggleLabel.setAttribute("for", toggleInput.id);
      toggleLabel.classList.add("toggle-label");

      const toggleInner = document.createElement("span");
      toggleInner.classList.add("toggle-inner");

      const activeText = document.createElement("span");
      activeText.classList.add("toggle-text", "active-text");
      activeText.textContent = "Active";

      const eliminatedText = document.createElement("span");
      eliminatedText.classList.add("toggle-text", "eliminated-text");
      eliminatedText.textContent = "Eliminated";

      toggleLabel.appendChild(toggleInner);
      toggleLabel.appendChild(activeText);
      toggleLabel.appendChild(eliminatedText);

      statusToggle.appendChild(toggleInput);
      statusToggle.appendChild(toggleLabel);

      teamHeader.appendChild(statusToggle);
    }

    teamWrapper.appendChild(teamHeader);

    // Team Content (to hold character slots)
    const teamContent = document.createElement("div");
    teamContent.classList.add("team-content");
    teamWrapper.appendChild(teamContent);

    // Create character slots
    createTeamSlots(teamContent, isUserDefense);

    // Append teamWrapper to teamDiv
    teamDiv.appendChild(teamWrapper);

    // Append teamDiv to contentDiv or zoneDiv depending on isUserDefense
    if (isUserDefense) {
      contentDiv.appendChild(teamDiv);
    } else {
      zoneDiv.appendChild(teamDiv);
    }
  }

  return zoneDiv;
}

// Create "Your Attacks" section
export function createYourAttacksSection() {
  const yourAttacksContainer = document.getElementById("yourAttacksContainer");
  yourAttacksContainer.innerHTML = "";

  const addAttackButton = document.createElement("button");
  addAttackButton.classList.add("button");
  addAttackButton.textContent = "Add Attack Team";
  addAttackButton.onclick = function () {
    addAttackTeam();
  };
  yourAttacksContainer.appendChild(addAttackButton);

  const attacksList = document.createElement("div");
  attacksList.id = "attacksList";
  yourAttacksContainer.appendChild(attacksList);
}

// Function to add an attack team
export function addAttackTeam(characters = null) {
  const attacksList = document.getElementById("attacksList");

  const attackDiv = document.createElement("div");
  attackDiv.classList.add("attack-team");

  // Create team div with class "team"
  const teamDiv = document.createElement("div");
  teamDiv.classList.add("team");

  /* --------------- Maybe remove this -------------------*/

  // Team Header
  const teamHeader = document.createElement("div");
  teamHeader.classList.add("team-header");

  // Add team label
  const label = document.createElement("label");
  const attackTeamNumber =
    attacksList.querySelectorAll(".attack-team").length + 1;
  label.textContent = `Attack Team ${attackTeamNumber}:`;
  teamHeader.appendChild(label);

  /* --------------------------------------------------------*/

  // Add a delete button for the attack team
  const deleteButton = document.createElement("button");
  deleteButton.type = "button";
  deleteButton.textContent = "Delete";
  deleteButton.classList.add("delete-attack-team-button");
  deleteButton.onclick = function () {
    // Remove characters from selectedUserCharacters
    const characterImage = teamDiv.querySelectorAll(".character-image");
    characterImage.forEach((img) => {
      const index = selectedUserCharacters.indexOf(img.alt);
      if (index > -1) {
        selectedUserCharacters.splice(index, 1);
      }
    });
    attacksList.removeChild(attackDiv);
  };
  teamHeader.appendChild(deleteButton);

  attackDiv.appendChild(teamHeader);

  // Team Content
  const teamContent = document.createElement("div");
  teamContent.classList.add("team-content");

  if (characters && characters.length > 0) {
    // If characters are provided, display them
    const charactersContainer = document.createElement("div");
    charactersContainer.classList.add("characters-container");

    characters.forEach((char) => {
      const slotDiv = document.createElement("div");
      slotDiv.classList.add("character-slot");
      const img = document.createElement("img");
      img.src = char.image;
      img.alt = char.name;
      img.classList.add("character-image");
      slotDiv.appendChild(img);
      charactersContainer.appendChild(slotDiv);
      // Add characters to selectedUserCharacters
      selectedUserCharacters.push(char.name);
    });
    teamContent.appendChild(charactersContainer);
  } else {
    // Otherwise, create empty character slots
    createTeamSlots(teamContent, true); // Assuming user's characters
  }

  teamDiv.appendChild(teamContent);
  attackDiv.appendChild(teamDiv);
  attacksList.appendChild(attackDiv);
}

// Function to add an attack team
function oldAttackTeam() {
  const attacksList = document.getElementById("attacksList");

  const attackDiv = document.createElement("div");
  attackDiv.classList.add("attack-team");

  // Create character slots
  const teamDiv = document.createElement("div");
  teamDiv.classList.add("team");
  createTeamSlots(teamDiv, true); // Assuming user's characters

  // Add a delete button for the attack team
  const deleteButton = document.createElement("button");
  deleteButton.textContent = "Delete";
  deleteButton.onclick = function () {
    attacksList.removeChild(attackDiv);
  };

  attackDiv.appendChild(teamDiv);
  attackDiv.appendChild(deleteButton);
  attacksList.appendChild(attackDiv);
}
