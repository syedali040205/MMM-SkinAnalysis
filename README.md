# MMM-SkinAnalysis

**MMM-SkinAnalysis** is a [MagicMirror²](https://magicmirror.builders/) module that performs real-time skin analysis using your webcam. It analyzes visible facial skin regions using computer vision techniques and provides feedback directly on the MagicMirror interface.

---

## 👥 Authors
- **Saniya Afzali** [profile](https://github.com/SaniyaAfzali)
- **Krishnahitha Jagannatham** [profile](https://github.com/KrishnahithaJagannatham)
- **Syed Mustafa Ayaan Ali**  

---

## 🧠 Features

- 🔍 Analyzes visible skin regions using webcam input
- 🖥 Displays real-time skin condition feedback on the mirror
- 💡 Designed to be lightweight and responsive
- 🛑 Can remain idle and activate on your defined logic

---

## 📦 Installation

1. Open your terminal and navigate to MagicMirror's `modules` folder:
   ```bash
   cd ~/MagicMirror/modules
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/MMM-SkinAnalysis.git
   ```

3. (Optional) Install dependencies if required:
   ```bash
   cd MMM-SkinAnalysis
   npm install
   ```

---

## ⚙️ Configuration

Add this module to the `modules` array in your `config/config.js` file:

```javascript
{
  module: "MMM-SkinAnalysis",
  position: "bottom_bar", // Or any preferred region
  config: {
    autoStart: true,           // Automatically run on mirror start (true/false)
    analysisInterval: 60000,   // Interval between automatic analyses (ms)
    analysisDuration: 5000     // Duration to display results (ms)
  }
}
```

---

## 🧪 How It Works

1. If `autoStart` is enabled, the module automatically performs skin analysis every X milliseconds.
2. Webcam input is captured and processed using image analysis techniques.
3. The module displays visual feedback like dryness, redness, or uneven tone indicators.
4. It automatically hides the analysis after the configured display duration.

---

## 🔐 Requirements

- Webcam connected to your MagicMirror device
- Node.js (for any backend logic, if used)
- Works on Raspberry Pi and Linux environments

---

## 🙋 FAQ

**Q: Does it analyze acne/oiliness/dryness?**  
A: Yes, the module performs basic visual analysis for features like texture, unevenness, and contrast. It is not a substitute for professional dermatology.

**Q: Can I control when analysis happens?**  
A: Yes! You can either use the `autoStart` config or hook it to external triggers like gestures, voice modules, or custom scripts.


---
## 📄 License

This project is licensed under the MIT License. See `LICENSE` for details.

🚫 Redistribution, rebranding, or showcasing this project in hackathons or academic evaluations or in anywhere this module is used without proper attribution is strictly prohibited.

You must provide visible credit in any derived project or demonstration, including:

Original author(s) name: Saniya Afzali,Krishnahitha Jagannatham,Syed Mustafa Ayaan Ali

GitHub URL: https://github.com/syedali040205/MMM-SkinAnalysis

violation of which will lead to strict legal action and license termination


---

## 💡 Notes

- Built for fun and experimental use.
