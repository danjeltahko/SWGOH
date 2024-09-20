// Import modules
import { initCharacterData } from "./suggestions.js";
import {
  updateForm,
  changeMode,
  toggleSidebar,
  submitForm,
} from "./form_handling.js";
import { savePresets, importPresets } from "./presets.js";

// Global Variables
window.mode = "3v3"; // Default mode
window.zonesConfig = {}; // Configuration for zones based on rank and mode
window.characterData = [];

// Initialize the application on page load
window.onload = function () {
  initCharacterData().then(() => {
    updateForm();
  });
};

// Expose functions to global scope
window.changeMode = changeMode;
window.toggleSidebar = toggleSidebar;
window.updateForm = updateForm;
window.submitForm = submitForm;
window.savePresets = savePresets;
window.importPresets = importPresets;
