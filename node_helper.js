const NodeHelper = require("node_helper");
const { spawn } = require("child_process");
const path = require("path");

module.exports = NodeHelper.create({
  start: function () {
    console.log("Skin Analysis Node Helper started");
  },

  socketNotificationReceived: function (notification, payload) {
    if (notification === "START_SKIN_ANALYSIS") {
      // We pass both script path & modelFile here
      this.startPythonScript(payload.pythonScriptPath, payload.modelFile);
    }
  },

  startPythonScript: function (pythonScriptPath, modelFile) {
    // Construct absolute paths based on this node_helper's location
    // so there's no confusion about relative paths.
    const scriptAbsolutePath = "/home/pi/MagicMirror/modules/MMM-SkinAnalysis/skin_analysis.py";
    const modelAbsolutePath = "/home/pi/MagicMirror/modules/MMM-SkinAnalysis/skin.h5";

    console.log("Starting Python script:", scriptAbsolutePath);
    console.log("Using model file:", modelAbsolutePath);

    // Spawn the Python process with two arguments:
    // 1) The .py script
    // 2) The model path
    const pythonProcess = spawn("python3", [scriptAbsolutePath, modelAbsolutePath]);

    // Capture standard output from Python
    pythonProcess.stdout.on("data", (data) => {
      const prediction = data.toString().trim();
      console.log("Prediction from Python:", prediction);
      // Send result back to the front-end module
      this.sendSocketNotification("SKIN_ANALYSIS_RESULTS", prediction);
    });

    // Capture any errors
    pythonProcess.stderr.on("data", (data) => {
      console.error("Error from Python script:", data.toString());
    });

    // Handle when Python process exits
    pythonProcess.on("close", (code) => {
      console.log(`Python process exited with code ${code}`);  // Corrected to use template literals
    });
  },
});
