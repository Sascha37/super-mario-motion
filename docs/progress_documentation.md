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

### 🧠 Game Options Considered
We evaluated different versions of Super Mario:

1. **Original Super Mario Bros. (via RetroArch)**  
   ✅ Predictable behavior  
   ✅ No source editing needed  
   ❗ Requires ROM and emulator

2. **Super Mario Bros. Remastered (Godot)**  
   ✅ Active development, modern visuals  
   ❗ Large codebase, needs modification for motion input

3. **Mario-Level-1 (Python 2 project)**  
   ✅ Easy to understand and extend  
   ❗ Outdated, limited to first level

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


## Week 5
### Progress (as of 04.11.2025)
- Implemented classes to handle motion detection via scikit-learn
- You can now collect, train and test your own gestures

### How to use collect and train
- Run `python collect.py --label <your label> --seconds <seconds to record>` to collect a gesture
- Run `python train.py` to train the model