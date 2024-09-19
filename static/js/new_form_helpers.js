// form_helpers.js

import {
  selectedUserCharacters,
  selectedOpponentCharacters,
} from "./character_selection.js";

// Collect teams from the form
export function collectTeams(containerId, isOpponentDefense = false) {
  const container = document.getElementById(containerId);
  const zones = container.querySelectorAll(".zone");
  const teamsData = {};

  zones.forEach((zone) => {
    const zoneId = zone.id;
    const prefix = isOpponentDefense ? "opponent_zone_" : "user_zone_";
    const zoneName = zoneId.replace(prefix, "");

    // For opponent's defense, check if the zone is included
    if (isOpponentDefense) {
      const zoneCheckbox = zone.querySelector(".zone-checkbox");
      if (zoneCheckbox && !zoneCheckbox.checked) {
        // Skip this zone
        return;
      }
    }

    const teams = zone.querySelectorAll(".team");
    teamsData[zoneName] = [];

    teams.forEach((team) => {
      const characters = [];
      const charSlots = team.querySelectorAll(".character-slot");

      charSlots.forEach((slot) => {
        const img = slot.querySelector(".character-image");
        if (img) {
          const charName = img.alt;

          // Find the character in characterData
          const character = window.characterData.find(
            (c) => c.name === charName,
          );

          if (character) {
            // Include the full character data
            characters.push({
              name: character.name,
              base_id: character.base_id,
              categories: character.categories,
              image: character.image,
            });
          } else {
            // Character not found in characterData
            console.warn(`Character not found in characterData: ${charName}`);
          }
        }
      });

      let eliminated = false;
      if (isOpponentDefense) {
        const checkbox = team.querySelector(".eliminated-checkbox");
        eliminated = checkbox.checked;
      }

      // Build the team data
      const teamData = {
        defense: characters,
      };

      if (isOpponentDefense) {
        teamData["eliminated"] = eliminated;
      }

      teamsData[zoneName].push(teamData);
    });
  });

  return teamsData;
}

// Display attack recommendations
export function displayAttackRecommendations(attackRecommendations) {
  for (const zoneName in attackRecommendations) {
    // Target opponent's defense zones
    const zoneDiv = document.getElementById(`opponent_zone_${zoneName}`);
    if (!zoneDiv) {
      console.warn(`Zone ${zoneName} not found in opponent's defense.`);
      continue;
    }

    const teams = attackRecommendations[zoneName];
    const teamDivs = zoneDiv.querySelectorAll(".team");

    teams.forEach((teamRecommendation, index) => {
      const teamDiv = teamDivs[index];
      if (!teamDiv) {
        console.warn(`Team ${index + 1} in zone ${zoneName} not found.`);
        return;
      }

      if (teamRecommendation && teamRecommendation.best_team) {
        // Remove previous recommendation if any
        const previousRecommendation = teamDiv.querySelector(
          ".attack-recommendation",
        );
        if (previousRecommendation) {
          previousRecommendation.remove();
        }

        // Wrap the defense team and attack recommendation in a container
        let teamWrapper = teamDiv.querySelector(".team-wrapper");
        if (!teamWrapper) {
          teamWrapper = document.createElement("div");
          teamWrapper.classList.add("team-wrapper");
          // Move existing content into the wrapper
          while (teamDiv.firstChild) {
            teamWrapper.appendChild(teamDiv.firstChild);
          }
          teamDiv.appendChild(teamWrapper);
        }

        const attackDiv = document.createElement("div");
        attackDiv.classList.add("attack-recommendation");

        // Create attack content
        const attackContent = document.createElement("div");
        attackContent.classList.add("attack-content");

        const teamHeader = document.createElement("h4");
        teamHeader.textContent = "Recommended Attack Team:";
        attackContent.appendChild(teamHeader);

        const charactersContainer = document.createElement("div");
        charactersContainer.classList.add("characters-container");

        teamRecommendation.best_team.attack.forEach((char) => {
          const img = document.createElement("img");
          img.src = char.image;
          img.alt = char.name;
          img.classList.add("character-image");
          charactersContainer.appendChild(img);
        });

        const winRate = document.createElement("p");
        winRate.textContent = `Win Rate: ${teamRecommendation.best_team.win_rate}%`;
        attackContent.appendChild(charactersContainer);
        attackContent.appendChild(winRate);

        // Add "Add to Your Attack" button
        const addButton = document.createElement("button");
        addButton.textContent = "Add to Your Attack";
        addButton.classList.add("add-to-attack-button");
        addButton.onclick = function () {
          addAttackTeam(teamRecommendation.best_team.attack);
        };

        attackContent.appendChild(addButton);

        attackDiv.appendChild(attackContent);

        // Append attackDiv to teamWrapper
        teamWrapper.appendChild(attackDiv);
      }
    });
  }
}

// Function to add the attack team to user's attack teams
function addAttackTeam(characters) {
  // Assuming you have a container for user's attack teams
  const userAttackContainer = document.getElementById("userAttackContainer");
  if (!userAttackContainer) {
    console.warn("User attack container not found.");
    return;
  }

  // Create a new team div
  const teamDiv = document.createElement("div");
  teamDiv.classList.add("team");

  // Create character slots and display characters
  const charactersContainer = document.createElement("div");
  charactersContainer.classList.add("characters-container");

  characters.forEach((char) => {
    const img = document.createElement("img");
    img.src = char.image;
    img.alt = char.name;
    img.classList.add("character-image");
    charactersContainer.appendChild(img);
  });

  teamDiv.appendChild(charactersContainer);
  userAttackContainer.appendChild(teamDiv);
}
