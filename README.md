**Veterinary Triage Assistant**
📌 *Project Overview*
The Veterinary Triage Assistant is a modern, Python-based desktop application designed to provide quick, rule-based triage guidance for pets. Whether for a veterinary clinic's front desk or concerned pet owners, this tool helps evaluate the urgency of an animal's symptoms in seconds. By answering a brief set of targeted questions, users receive an immediate severity assessment and a breakdown of why that result was given.

✨ *Key Features*
Multi-Species Support: Tailored symptom assessment for dogs, cats, birds, rabbits, and other small animals.

Interactive Diagnostic Questionnaire: Evaluates critical health indicators such as overall symptom severity, alertness levels, appetite, and breathing difficulty.

Transparent Scoring: Features a "Details" dashboard that provides a severity weight breakdown and an explanation ("Why this result?") for the generated triage level.

Session History: Keeps track of previous diagnoses during the session for quick reference.

Modern, Responsive UI: Built with CustomTkinter, featuring a polished interface, responsive image scaling with baked-in text overlays, and seamless Light/Dark mode toggling.

🛠️ *Technology Stack*
Language: Python 3.x

GUI Framework: customtkinter (for a modern, customizable, and flat-design interface)

Image Processing: Pillow (PIL) for dynamic image cropping, gradient overlays, and responsive typography rendering.

📂 *Project Structure*
App.py: The main application entry point, handling the window initialization, navigation bar, responsive home page, and state management.

UI.py: Contains the logic and layout for the inner pages (Diagnosis form and Details dashboard) as well as the triage evaluation rules.

assert/: Directory for application assets (e.g., background images, icons).
