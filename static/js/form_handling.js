// form_handling.js

import { createZone, createYourAttacksSection } from "./zone_creation.js";
import {
  collectAttackTeams,
  collectTeams,
  displayAttackRecommendations,
} from "./form_helpers.js";

// Configurations for teams per zone based on rank and mode
export const configurations = {
  kyber: {
    "3v3": { T1: 5, B1: 5, B2: 5 },
    "5v5": { T1: 3, B1: 4, B2: 4 },
  },
  aurodium: {
    "3v3": { T1: 3, B1: 3, B2: 3 },
    "5v5": { T1: 5, B1: 4, B2: 4 },
  },
  chromium: {
    "3v3": { T1: 4, B1: 3, B2: 3 },
    "5v5": { T1: 2, B1: 2, B2: 3 },
  },

  bronzium: {
    "3v3": { T1: 3, B1: 2, B2: 2 },
    "5v5": { T1: 1, B1: 2, B2: 2 },
  },

  carbonite: {
    "3v3": { T1: 1, B1: 1, B2: 1 },
    "5v5": { T1: 1, B1: 1, B2: 1 },
  },
};

// Update form based on mode and rank
export function updateForm() {
  const rank = document.getElementById("rank").value;
  window.zonesConfig = configurations[rank][window.mode];

  // Generate opponent's defense zones
  const zonesContainer = document.getElementById("zonesContainer");
  zonesContainer.innerHTML = ""; // Clear previous content

  // Create Zones for the opponent's defense
  zonesContainer.appendChild(createZone("T1", window.zonesConfig.T1, false));
  zonesContainer.appendChild(createZone("B1", window.zonesConfig.B1, false));
  zonesContainer.appendChild(createZone("B2", window.zonesConfig.B2, false));

  const userDefenseContainer = document.getElementById("userDefenseContainer");
  userDefenseContainer.innerHTML = "";

  // Create Zones player
  userDefenseContainer.appendChild(
    createZone("T1", window.zonesConfig.T1, true),
  );
  userDefenseContainer.appendChild(
    createZone("B1", window.zonesConfig.B1, true),
  );
  userDefenseContainer.appendChild(
    createZone("B2", window.zonesConfig.B2, true),
  );

  // Update user's defense teams
  // createUserDefense();

  // Create "Your Attacks" section
  createYourAttacksSection();
}

// Change mode between 3v3 and 5v5
export function changeMode(selectedMode) {
  window.mode = selectedMode;
  updateForm();
}

// Toggle sidebar visibility
export function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  sidebar.classList.toggle("closed");
}

// Submit form and handle calculation
export function submitForm(event) {
  event.preventDefault();

  // Collect data from the form and sidebar
  const allyCode = document.getElementById("allyCode").value;
  const minGear = document.getElementById("minGear").value;
  const mode = document.querySelector('input[name="mode"]:checked').value;
  const rank = document.getElementById("rank").value;

  // Collect user's defense teams
  const userDefense = collectTeams("userDefenseContainer");

  // Collect user's attack teams
  const userAttack = collectAttackTeams();

  // Collect opponent's defense teams
  const opponentDefense = collectTeams("zonesContainer", true);

  // Prepare data to send
  const data = {
    allyCode: allyCode,
    minGear: minGear,
    mode: mode,
    rank: rank,
    userDefense: userDefense,
    userAttack: userAttack,
    opponentDefense: opponentDefense,
  };

  // Display loading indicator
  const loadingIndicator = document.createElement("div");
  loadingIndicator.classList.add("loading-indicator");
  loadingIndicator.textContent = "Calculating...";
  const mainContent = document.querySelector(".main-content");
  mainContent.appendChild(loadingIndicator);

  // Disable the Calculate button
  const calculateButton = document.querySelector('input[value="Calculate"]');
  calculateButton.disabled = true;

  // Send data to the server
  fetch("/calculate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((result) => {
      // Remove loading indicator
      mainContent.removeChild(loadingIndicator);
      // Enable the Calculate button
      calculateButton.disabled = false;

      // Display the attack recommendations under each opponent's defense team
      displayAttackRecommendations(result.attackRecommendations);
    })
    .catch((error) => {
      console.error("Error calculating attack teams:", error);
      // Remove loading indicator
      mainContent.removeChild(loadingIndicator);
      // Enable the Calculate button
      calculateButton.disabled = false;
      alert("An error occurred while calculating attack teams.");
    });
}
