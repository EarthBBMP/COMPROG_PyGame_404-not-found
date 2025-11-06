# How to Install Git, Clone This Project, and Run the Game

Follow these steps if you have never used Git or Python before.  
Works on **Windows** and **Mac**.

---

## 1. Install Git

### Windows
1. Go to: https://git-scm.com/download/win  
2. Download and run the installer  
3. Keep all default settings  
4. Finish installation

Verify Git by running (in Command Prompt):
git --version

### Mac
Open Terminal and run:
git --version

If Git is not installed, macOS will prompt to install Command Line Tools — click **Install**.

---

## 2. Install Python

Download Python from:
https://www.python.org/downloads/

### Windows
When installing, **check “Add Python to PATH”**.

### Mac
Install normally.

Verify Python:
python --version
or
python3 --version

---

## 3. Install Pygame

### Windows
pip install pygame

### Mac
python3 -m pip install pygame

---

## 4. Clone this project

Open Command Prompt (Windows) or Terminal (Mac), then run:
git clone https://github.com/EarthBBMP/COMPROG_PyGame_404-not-found

---

## 5. Enter the project folder

cd COMPROG_PyGame_404-not-found

---

## 6. Run the game

### Windows
python game.py

### Mac
python3 game.py

A game window should open.

---

## Controls

- A / ← : Move left  
- D / → : Move right  
- E : Interact  
- ESC : Close quest  

---

## ✅ Troubleshooting

**“git: command not found”**  
Reinstall Git.

**“pygame not found”**  
Run:
pip install pygame

**“python not found”**  
Reinstall Python and ensure Windows users check **Add Python to PATH**.

**Game closes instantly**  
Run from terminal with:
python game.py
(or python3 game.py on Mac)

---

Done — you can now run and edit the game.
