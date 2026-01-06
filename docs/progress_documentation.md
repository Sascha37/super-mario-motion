# Progress Documentation - Play Super Mario with Your Body

## Week 0 (Before the start of the semester)

Before the semster started, we held our first meeting, in which we were briefed on what the project
entails.

`"Create an Application to control Super Mario with your body"`

Over the next two weeks, we had to think about:

- "What **technology** should we use?"
- "Should we write our own game or use an existing implementation?"
- "How do we **capture our image** from our webcam and let the computer interpret it in real time?"
- "How does our program **communicate to the game** that we want to perform an action?"

---

## Week 1 (29.09.25 - 07.10.25)

- Agreed to use **Python** as our programming language for this project, manly due to:
    - all three of us developing on different operating systems
    - robust selection of machine learning and computer vision libraries (OpenCV, Mediapipe, NumPy)

- Played through multiple versions of the game "Super Mario Bros.", some official, some fanmade. In
  the end we had three options left to pick from:

| Game                                                                                                        | Pros                                                                                          | Cons                                                                                                                                          |
|-------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| The original Super Mario Bros.                                                                              | + The mechanics of the game are well documented<br>+ We do not need to change the source code | - Needs an emulator and rom to run                                                                                                            |
| ["Mario-Level-1" (Python 2 Project using pygame)]("https://github.com/justinmeister/Mario-Level-1")         | + Easy to understand and extend if needed                                                     | - Has not been updated since 11 years<br>- Runs on python 2, so our newer ml modules might not work<br>- Only has the first level of the game |
| ["Super Mario Bros. Remastered (Godot)]("https://github.com/JHDev2006/Super-Mario-Bros.-Remastered-Public") | + Very new and actively developed<br>+ Modernized visuals                                     | - Codebase is too big<br>- Code would need modification to add motion controls                                                                |

The original Super Mario Bros. won. The goal for the next week was to play through the game
multiple times and figure out every possible type of input that the game needs to be completed.

---

## Week 2 (07.10.25 - 14.10.25)

After we have decided to use the original Super Mario. Bros as our game, we had to find out what
every single action can be performed in game to play it from start to finish.

This is an image of the controller used to play the game on the Nintendo Entertainment System. In
the next section we will reference the buttons of this controller.

| ![Image of an NES Controller](https://upload.wikimedia.org/wikipedia/commons/3/30/Nes_controller.svg) | 
|:-----------------------------------------------------------------------------------------------------:| 
|                                     *Image of an NES controller*                                      |

### Controls

| Action                 |                     Button                     | Explanation                                                                                                                                                                                                                                                                             |
|------------------------|:----------------------------------------------:|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Start + Pause the game |                     START                      | The game can be paused and resumed at any time by pressing START.                                                                                                                                                                                                                       |
| Select Menu Option     |                     SELECT                     | Only needed at the start of the game, each press of the SELECT button changes the selected menu option.                                                                                                                                                                                 |
| Jump                   |                       A                        | A jump can be performed while Mario is on the ground and while he is in a crouching state. You can influence jump height depending on how long the A-Button is held. While airborne pressing either LEFT or RIGHT will shift the momentum of Mario.                                     |
| Swimming               |                       A                        | Some levels in this game are water levels, instead of jumping, Mario will swim by pressing the A-Button. To not sink in the water, the player has to repeatedly press the A-Button, to swim up a fixed distance.                                                                        |
| Walking and Running    | LEFT, LEFT + B (held), RIGHT, RIGHT + B (held) | Pressing either RIGHT or LEFT will make Mario walk in the desired direction. If you hold the B-Button alongside a directional input, Mario will run.                                                                                                                                    |
| Crouching              |                      DOWN                      | Mario can crouch while he is on the ground and is in his BIG MARIO state. This allows him to dodge enemies and go through tight openings that BIG MARIO normally would not fit in. If Mario is above the entrance of a Warp Pipe, he can enter it by crouching, regardless of his size. |
| Throw Fireball         |                       B                        | While grounded or airborne, if Mario has the Fire Flower powerup, he can throw fireballs by repeatedly tapping the B-Button.                                                                                                                                                            |

---

## Week 3 (14.10.25 - 21.10.25)

In week 3 we started writing code, after we spent the first two weeks researching.

- Started using **GitHub Issues** for project planning and tracking what needs to be done.
- Used **MediaPipe** alongside **OpenCV** to draw a skeleton over the webcam image.
- Brainstormed which motions we would perform for different inputs in game.
- Developed our own GUI, with a menu option to toggle features like whether to display the
  skeleton. Alongside a display that shows the current detected pose with a small image,
  representing each pose.
- **Milestone: Mario would walk forward by holding up our right hand!**

---

## Week 4 (21.10.25 - 28.10.25)

- Identified and documented a bug where on some operating systems the thread would not properly
  close upon termination
- We now had motion inputs. However, right now they are being calculated using the coordinates of
  the landmarks (nodes on the skeleton graph), we call this the "**simple mode**", designed to be
  used without training data and from a sitting position. For the next week we looked into machine
  learning modules to predict **full body motions**. Scikit-learn seemed like the go-to solution
  for this kind of problem in Python.
- Designed an image of a NES controller, planned to display what buttons are currently pressed,
  giving the user a visual indicator on what is going on.
- **Milestone: It was now possible to play through the first level of Super Mario Bros. just with
  your body.**
    - This was possible by having dedicated inputs for walking, running and jumping
    - Considerable time was spent fine-tuning how motions would result in different buttons being
      pressed. Like, for example, when transitioning from walking to standing that we have the
      program press the button of the opposite direction to stop Mario’s momentum.

---

## Week 5 (28.10.25 - 04.11.25)

- Fixed bugs relating to issues with thread termination, while doing so we discovered more issues
- Extended our GUI
    - Added a **mode selector**, allowing users to switch between `simple` and `full-body` motion
      recognition.
    - Added a **preview selector**, changing the way the webcam image is displayed to the user.
      Available option are: `Webcam`, `Webcam + Skeleton`, `Skeleton Only`
    - Added a `Debug Info` checkbox, to be able to display debug information of the screen without
      being reliant on terminal output
- Identified a major issue: Currently now our loop, that we are using to update UI-elements and
  exchange information between Modules has a delay of 1ms. Tkinter only runs the function when it
  has the time to do so, meaning that 1 ms is the minimum possible delay, in practice, the actual
  interval is even longer depending on hardware and other factors outside our control. This is not
  sufficient if we want to send inputs to a video game in real time.
    - Potential solution: Only use our update function in main to update UI-elements.
        - Introduce a new module called state.py, containing variables for the current pose, images
          from OpenCV etc. The module will have getter and setter, so that our modules can
          communicate with each other without going through our previous delayed loop.
        - One concern will be race conditions, but for the moment every module only writes to their
          dedicated variables, this should not cause issues in our current implementation.
- **Milestone: The program can now detect full-body motions based on the training data we provide.
  **

---

## Week 6 (04.11.25 - 11.11.25)

This week focused mainly on four things:

- **Updated the README.md** file to better fit the current state of our project
    - Added issue templates to make it easier to write issues
    - There are also now detailed explanations on how to start up the application on different
      operating systems
- Fixed a couple of minor visual bugs that we had listed in our GitHub Issues
- **Refactored every module** to change the way they communicate with each other
    - `state.py` was implemented allowing modules to write and retrieve information via getter and
      setter functions of the module
    - This makes the responsiveness of the program no longer reliant on the slow main-loop of
      Tkinter
- **Milestone: Allow training data to be captured directly from within the application.** We
  implemented a new mode called "Collect Mode". This mode does the following:
    - The interface stops displaying information not related to the capture process, while
      automatically enabling Debug mode.
    - A new "**Start collecting**" button and guidelines und what actions to perform appear.
      Clicking on it will **start an automated data collection process** to directly capture
      training data from within the application:
        - The GUI shows a countdown, then records a series of predefined poses for a set duration.
        - A visible **recording countdown** now runs while capturing data.
        - Live webcam preview and debug landmarks remain active during collection, allowing the
          user to check if they are performing the motions correctly.

---

## Week 7 (11.11.25 - 18.11.25)

This week’s changes once again mostly happened on the backend. We worked on

- GUI now **starts in the middle of our screen** on Windows and macOS systems
- **Fixed the collect mode** of our Application to now work on Windows and Linux without any
  issues. Also added a “Stop”-Button to cancel out early
- **Changed folder structure** of our project to follow standards
- **Redrew old and added missing symbols**, representing all possible poses (not yet implemented in
  the application)
- **Started using pytest** to test our code (goal being that they are implemented in GitHub Actions
  and ran on every PR before merging)
- Refactored almost every module according to the PEP 8 Python Style Guide to make sure our code
  will be maintainable and readable for the next few months (and hopefully years)
- **Two big milestones:**
    - **The game is now playable in `full-body` mode!**
    - **The pose detection logic in `simple-mode` is finished**

---

## Week 8 (18.11.25 - 25.11.25)

For this week, we were making sure that users using our application dont get overwhelmed by
creating a dedicated help page. Goal for this and the coming weeks are making our code as
readable and extensible as possible. And on the user side making sure that there is no
confusion using the program.

- Pytest is now fully implemented in our project
  - Started developing **additional tests**
- **Refactored code** to adhere to PEP 8 style guide
- Added a **batch file to comfortably start the program** from outside of the terminal / IDE on
  Windows
- We can now press a button in our app to start the game 
- Created a **help page** directed at users to learn how to use the application, can be opened
  from within the app
- The **virtual gamepad now displays the currently pressed inputs**
  - Made it easier to sort collected data, also started collecting good permanent data, our
  goal is that we can ship the application with a working pre trained model
  
---

## Week 9 (25.11.25 - 02.12.25)

This week we had a huge stack of tasks that we were sure would take at least more than a week.
But we managed work through them all. With that our program ist mostly feature complete.

- Pytest is now integrated into **GitHub Actions**
- **Collected a lot of training data** from multiple different people
- Finished our input module, by **adding the last pose to button mapping**
- **Improved performance** by removing duplicate ressource intensive tasks
- Wrote **docstrings** for each functions, that can be **generated into a docs webpage** using Sphinx
- Restructured our project that **PyInstaller** could be used to build a standalone
  **executable file** on Windows, macOS and Linux
- Our **program now has a json config**, it gets created if it doesn’t exist and stores data that
  can be kept between different sessions of the program
- Extended the way we parse inputs by allowing **multiple control schemes**, that can be selected
  via a dropdown menu
- It is now possible to **play the game by launching an external website** containing the game
- **Added an app icon** that displays in the lop left of our UI and taskbar

---

## Week 10 (02.12.25 - 09.12.25)

- **Fixed our train script** to work again, by changing the path where to look for training data.
- The config now gets **created with default paths** where the emulator is likely installed.
- Made the **collect mode use the full screen** to better see instructions from far away.
- **Updated README** and the **help page** to better reflect the state of our project.
- Fixed the issue with camera permissions on macOS systems not being granted.
  - **We now have a startup screen** where everything gets loaded and the user on mac is asked to grant camera permissions.
- When writing more tests, we realized that one function was calculating incorrect numbers. We fixed the function, but had to abandon the previous training data.
  - We already have **collected a new set of training data**.
  
---

## Week 11 (09.12.25 - 16.12.25)

- Got **others to test the application** and got some **valuable feedback**
  - Took notes of all bugs and issues
- Readme and help page now includes **more information**, making it easier for others to set up the project
- We looked into ways to have a better model.
  - In the end we kept on using the same model as before
- Added a **warning inside of the program**, if the config is invalid
- **Made our pose recognition logic better**, by deciding the pose based on a majority vote and other performance related enhancements
- **Fixed an issue** where the program would not send keystrokes correctly on windows with certain keyboard layouts

## Weeks 12-14 (16.12.25 - 06.01.26)
University winter break started during this timeframe (22.12.25 - 06.01.26).
We still managed to get a few important things done.

- Made our code **more readable** by setting up Ruff to detect magic numbers so that we could fix them
- **Got feedback** from another person and usability problems that occurred have been noted and fixed
- **Added a reload config button** to reload the config instantly instead of reopening the program
- We now have a **camera selector** inside of our application
- Created a new module to create a **report on how well a model performs**
- **Tested different algorithms** for our classifier and created graphs showing how each performs. The algorithms we tested were: SVC, KNN, Decision Tree, Random Forest