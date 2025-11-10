# Play Super Mario with Your Body Motion – Progress Documentation

## Preparation Before Semester Start
After our first meeting regarding the project, we designed a rough outline of what we first need to do.  
This included:
- Deciding how we want to send our inputs to the game  
- Thinking about which motions we want to use for each input  
- Choosing which version of the game we want to use  

---

## Week 1  
*Initial Project Planning*

- Defined the main project goal: controlling Super Mario using body motions.
- Discussed technical approaches for motion detection and how inputs would be translated into game controls.
- Decided to use **Python** as the primary language for input simulation and motion processing.
- Created an initial plan for project structure and next steps.

---

## Week 2
*Designing Controls and Evaluating Game Options*

### Mario Game Controls
We analyzed how the original game handles player input and mapped them to possible body motions:

- **Menu Controls:**  
  - `START` – choose option  
  - `SELECT` – switch between options

- **Jump / Swim:**  
  - `A` button – jump or swim (depending on state)  
  - Holding `A` – higher jump  
  - `LEFT` / `RIGHT` – air control  
  - Swim has fixed distance → might require separate motion input

- **Walking / Running:**  
  - `LEFT` / `RIGHT` – walk  
  - Hold `B` – run (faster movement)

- **Crouch / Pipe Entry:**  
  - `DOWN` – crouch (only Big Mario) or enter pipe

- **Crouch Jump:**  
  - `DOWN` + `A` – jump out of small spaces

- **Throw Fireball:**  
  - `B` – throw a fireball (tap repeatedly for rapid fire)

### Game Options Considered
We evaluated different versions of Super Mario:

1. **Original Super Mario Bros. (via RetroArch)**  
   \+ Predictable behavior  
   \+ No source editing needed  
   \- Requires ROM and emulator

2. **Super Mario Bros. Remastered (Godot)**  
   \+ Active development, modern visuals  
   \- Large codebase, needs modification for motion input

3. **Mario-Level-1 (Python 2 project)**  
   \+ Easy to understand and extend  
   \- Outdated, limited to first level

We decided to use version 1 because it runs the best and is the most stable and reliable option.
### Tools and Libraries
- **PyAutoGUI** – to simulate keyboard inputs  
- **OpenCV + MediaPipe** – to capture and interpret webcam motion

### Mockup
- Created the first mockup of the user interface.

---

##  Week 3 
*Implementation Progress and First Steps*

### Progress (as of 20.10.2025)
- Started using **GitHub Issues** for project planning and task tracking.  
- Integrated **OpenCV** and **MediaPipe** for motion detection support.  
- Brainstormed which specific motions we want to recognize for each control input.  
- Developed a **GUI with toggle switches** to enable or disable features.  
- Added an **indicator for detected gestures** within the interface.
- Implemented our **first gesture** and integrated it into the program to **test if the motion-based control works**. 

### Next Steps
- Implement **PyAutoGUI** to send simulated keypresses to the game.  
- Develop and fine-tune the **motion recognition logic**.

---

## Next Steps (Planned for Upcoming Weeks)
- Finalize motion detection mappings and gestures.  
- Complete integration of PyAutoGUI with motion recognition.  
- Begin testing gameplay with motion-based controls.  
- Optimize gesture detection for accuracy and performance.

## Week 4
### Progress (as of 28.10.2025)
- Successfully completed the first level (World 1-1) of Super Mario Bros. **entirely via body motion controls**.  
  - Walking/running left and right and jumping all work through motion input.  
  - Considerable time was spent fine-tuning motion transitions for natural gameplay (e.g., counter-inputs to stop Mario’s momentum).
- Fixed issues in motion-to-input responsiveness to make controls feel intuitive.
- Encountered a thread termination issue on one machine — still under investigation.
- Added initial **debugging tools** and **interface planning** for easier tracking of in-game actions.
- Started researching **scikit-learn’s RandomForestClassifier** for improved motion recognition.
- Planned the addition of a **visual virtual gamepad** in the GUI that highlights pressed buttons.

**Next Steps**
- Finish adding all remaining poses for full-body motion.
- Integrate the RandomForest model for classification.
- Expand the GUI with debug and visualization tools.

---

## Week 5
### Progress (as of 04.11.2025)

This week we focused on stability, full-body control, and usability:

- **Thread Management:**  
  Fixed thread shutdown issues when the program closes.  
  Identified and documented several bugs for follow-up.
- **Full-Body Motion Controls:**  
  Expanded motion recognition to support full-body gestures captured from webcam input.  
  This marks the start of the project’s main functional phase.
- **New User Interface:**  
  Added a **mode selector** allowing users to switch between *Simple* and *Full-body* modes.  
  Added a **preview selector** (`Webcam`, `Webcam + Skeleton`, `Skeleton Only`).  
  Added a **Debug Info** checkbox for showing/hiding additional information.

**Latency Issue**
- Tkinter’s `.after()` loop for updating UI elements introduced noticeable latency (minimum 1 ms delay, longer in practice).
- Designed a new architecture using a `state.py` module to handle shared data between threads (`vision`, `input`, `main`) without delay.
- This module will use getters and setters to prevent race conditions and streamline communication.

**Next Steps**
- Refactor information exchange between modules to remove latency.
- Update the project README.
- Extend the GUI for easier gesture data collection.
- Add the virtual gamepad visualization.

---

## Week 6
### Progress (as of 11.11.2025)

This week focused on improving the GUI and integrating a streamlined data collection mode:

- Added a new **Collect Mode** to the GUI, selectable in the mode dropdown alongside “Simple” and “Full-body”.
- In Collect Mode:
  - The interface switches to a minimal layout.
  - Debug mode is automatically enabled.
  - Non-essential widgets (pose display, send-inputs checkbox, etc.) are hidden.
  - A new **Start Collecting** button and **status text area** appear below the debug info.
- Implemented an **automatic data collection sequence**:
  - The GUI shows a countdown, then records a series of predefined poses for a set duration.
  - A visible **recording countdown** now runs while capturing data.
- Live webcam preview and debug landmarks remain active during collection.
- Improved cross-platform GUI layout (macOS/Linux) to ensure all content fits properly.
- Fixed color and spacing inconsistencies and removed unwanted white borders around buttons.