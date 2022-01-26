# knight-board
Cloudstaff Exam

### Pre-requisites
- Python

### Usage
- In the moves.txt, add movesets in between the `GAME-START` and `GAME-END` strings
- The format of the movesets should be `<COLOR>:<DIRECTION>`
- COLORS: `R,B,Y,G` (red, blue, yellow, green) and DIRECTIONS: `N,E,W,S` (north, east, west, south)
- After adding desired move sets, run the `examcloudstaff.py` with `python examcloudstaff.py`
- You should be able to see what happened to the Knights at final_state.json file

### Developer Notes
- There are print statements to see a bit of logs on what happened on the board
- There's also a visual grid on the logs after running the script
- For state management, I was looking into using pickle but decided to use a GLOBAL variable that stores the object states
- Some code can be moved to reusable functions, but needed to submit this ASAP