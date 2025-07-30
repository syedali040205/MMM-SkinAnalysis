/* MagicMirror Module: MMM-SkinAnalysis
 * See github.com/your-repo
 */
Module.register("MMM-SkinAnalysis", {
  // Default config options
  defaults: {
    pythonScriptPath: "/home/pi/MagicMirror/modules/MMM-SkinAnalysis/skin_analysis.py",
    modelFile: "skin.h5",
    updateInterval: 10000, // Check/update every 10 seconds
    cameraResetDelay: 3000 // Delay before switching back to Face Recognition
  },

  start: function () {
    console.log("Starting MMM-SkinAnalysis");
    this.prediction = "Initializing...";

    // Send the script path & model name to the node helper
    this.sendSocketNotification("START_SKIN_ANALYSIS", {
      pythonScriptPath: this.config.pythonScriptPath,
      modelFile: this.config.modelFile
    });

    // Start user detection loop
    this.detectUserPresence();
  },

  //  Monitor user presence and switch modules when no user is detected
  detectUserPresence: function () {
    var self = this;
    setInterval(() => {
      self.sendSocketNotification("CHECK_USER_PRESENCE");
    }, 5000); // Check every 5 seconds
  },

  //  Handle incoming notifications from the node helper
  socketNotificationReceived: function (notification, payload) {
    if (notification === "SKIN_ANALYSIS_RESULTS") {
      this.prediction = payload;
      this.updateDom();
    }

    // If no user is detected, switch back to Face Recognition
    if (notification === "NO_USER_DETECTED") {
      console.log("No user detected. Restarting Face Recognition...");

      //  Release the camera before restarting Face Recognition
      this.sendNotification("RELEASE_CAMERA");

      setTimeout(() => {
        this.sendNotification("START_FACE_RECOGNITION");
      }, this.config.cameraResetDelay);
    }
  },

  // Generate the DOM for this module
  getDom: function () {
    const wrapper = document.createElement("div");
    wrapper.className = "skin-analysis-wrapper";
    wrapper.innerHTML = `<strong>Prediction:</strong> ${this.prediction}`;
    return wrapper;
  },

  // Load custom CSS
  getStyles: function () {
    return ["styles.css"];
  }
});