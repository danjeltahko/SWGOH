// zone_creation.js

import { createTeamSlots } from "./character_selection.js";

// Create a zone (used for both user's defense and opponent's defense)
export function createZone(zoneName, numTeams, isUserDefense) {
  const zoneDiv = document.createElement("div");
  zoneDiv.classList.add("zone");

  // Assign unique IDs
  if (isUserDefense) {
    zoneDiv.id = `user_zone_${zoneName}`;
  } else {
    zoneDiv.id = `opponent_zone_${zoneName}`;
  }

  const zoneHeader = document.createElement(isUserDefense ? "h4" : "h3");
  zoneHeader.textContent = `Zone ${zoneName}`;
  zoneDiv.appendChild(zoneHeader);

  for (let i = 1; i <= numTeams; i++) {
    const teamDiv = document.createElement("div");
    teamDiv.classList.add("team");

    const teamHeader = document.createElement("div");
    teamHeader.classList.add("team-header");

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

    teamDiv.appendChild(teamHeader);

    // Create character slots
    createTeamSlots(teamDiv, isUserDefense);

    zoneDiv.appendChild(teamDiv);
  }

  return zoneDiv;
}

// Create user's defense teams
export function createUserDefense() {
  const userDefenseContainer = document.getElementById("userDefenseContainer");
  userDefenseContainer.innerHTML = "";

  for (const zoneName in window.zonesConfig) {
    const numTeams = window.zonesConfig[zoneName];

    const zoneDiv = document.createElement("div");
    zoneDiv.classList.add("zone");
    zoneDiv.id = `zone_${zoneName}`;

    const zoneHeader = document.createElement("h4");
    zoneHeader.textContent = `Zone ${zoneName}`;

    const arrowSpan = document.createElement("span");
    arrowSpan.classList.add("collapse-arrow");
    arrowSpan.textContent = "▼"; // Down arrow

    zoneHeader.appendChild(arrowSpan);
    zoneHeader.classList.add("collapsible");

    const contentDiv = document.createElement("div");
    contentDiv.classList.add("zone-content");

    zoneHeader.onclick = function () {
      contentDiv.classList.toggle("collapsed");
      // Toggle arrow direction
      if (contentDiv.classList.contains("collapsed")) {
        arrowSpan.textContent = "►"; // Right arrow
      } else {
        arrowSpan.textContent = "▼"; // Down arrow
      }
    };

    for (let i = 1; i <= numTeams; i++) {
      const teamDiv = document.createElement("div");
      teamDiv.classList.add("team");

      const label = document.createElement("label");
      label.textContent = `Team ${i}:`;
      teamDiv.appendChild(label);

      createTeamSlots(teamDiv, true);

      contentDiv.appendChild(teamDiv);
    }

    zoneDiv.appendChild(zoneHeader);
    zoneDiv.appendChild(contentDiv);
    userDefenseContainer.appendChild(zoneDiv);
  }
}

// Create "Your Attacks" section
export function createYourAttacksSection() {
  const yourAttacksContainer = document.getElementById("yourAttacksContainer");
  yourAttacksContainer.innerHTML = "";

  const addAttackButton = document.createElement("button");
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
function addAttackTeam() {
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
