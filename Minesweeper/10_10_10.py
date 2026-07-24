import requests
import time
import sys

API_KEY = "minesweeper_3918d2f61f5e490a811922b50006712f"
SESSION_ID = "47832654-218d-4339-b6bc-c1c87b0e111c"
BASE_URL = "https://agent.aiplayground.ir/api"


def get_session():
    try:
        res = requests.get(f"{BASE_URL}/sessions/{SESSION_ID}/")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Connection failure: {e}")
        time.sleep(1)
        return None


def play_move(action, row, col):
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "action": action,
        "row": row,
        "col": col
    }
    try:
        res = requests.post(f"{BASE_URL}/games/minesweeper/move/", headers=headers, json=payload)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error executing action {action} at ({row}, {col}): {e}")
        return None



def deduce_moves(grid, R, C):
    equations = []

    for r in range(R):
        for c in range(C):
            val = grid[r][c]
            if val.isdigit():
                num = int(val)
                hidden_neighbors = []
                flagged_count = 0

                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < R and 0 <= nc < C:
                            if grid[nr][nc] == "hidden":
                                hidden_neighbors.append((nr, nc))
                            elif grid[nr][nc] == "flagged":
                                flagged_count += 1

                mines_left = num - flagged_count
                if hidden_neighbors:
                    equations.append({'set': set(hidden_neighbors), 'val': mines_left})

    known_safe = set()
    known_mines = set()

    for eq in equations:
        if eq['val'] == 0:
            for cell in eq['set']:
                known_safe.add(cell)
        elif eq['val'] == len(eq['set']):
            for cell in eq['set']:
                known_mines.add(cell)

    if known_safe or known_mines:
        return known_safe, known_mines


    for i in range(len(equations)):
        for j in range(len(equations)):
            if i == j:
                continue
            eq1 = equations[i]
            eq2 = equations[j]

            if eq1['set'].issubset(eq2['set']):
                diff_set = eq2['set'] - eq1['set']
                diff_val = eq2['val'] - eq1['val']

                if diff_set:
                    if diff_val == 0:
                        for cell in diff_set:
                            known_safe.add(cell)
                    elif diff_val == len(diff_set):
                        for cell in diff_set:
                            known_mines.add(cell)

    return known_safe, known_mines


def get_safest_guess(grid, R, C):
    cell_risks = {}
    for r in range(R):
        for c in range(C):
            if grid[r][c] == "hidden":
                cell_risks[(r, c)] = []

    for r in range(R):
        for c in range(C):
            val = grid[r][c]
            if val.isdigit():
                num = int(val)
                hidden_neighbors = []
                flagged_count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < R and 0 <= nc < C:
                            if grid[nr][nc] == "hidden":
                                hidden_neighbors.append((nr, nc))
                            elif grid[nr][nc] == "flagged":
                                flagged_count += 1
                if hidden_neighbors:
                    eq_risk = (num - flagged_count) / len(hidden_neighbors)
                    for cell in hidden_neighbors:
                        if cell in cell_risks:
                            cell_risks[cell].append(eq_risk)

    final_risks = {}
    for cell, risks in cell_risks.items():
        if risks:
            final_risks[cell] = sum(risks) / len(risks)
        else:
            final_risks[cell] = 0.1

    safest_cell = min(final_risks, key=final_risks.get)
    return safest_cell




if __name__ == "__main__":
    print(f"Starting Logical Minesweeper Agent (Session: {SESSION_ID})")

    while True:
        data = get_session()
        if not data:
            continue

        state = data["state"]
        grid = state["grid"]
        R = len(grid)
        C = len(grid[0])

        if state["game_over"]:
            if state.get("victory"):
                print("VICTORY! Minesweeper solved successfully using Logic & Probability!")
            else:
                print("GAME OVER. Exploded on a mine.")
            break

        all_hidden = all(grid[r][c] == "hidden" for r in range(R) for c in range(C))
        if all_hidden:
            start_r, start_c = R // 2, C // 2
            print(f"First-click Safety: Revealing center cell ({start_r}, {start_c})")
            play_move("reveal", start_r, start_c)
            time.sleep(0.5)
            continue

        known_safe, known_mines = deduce_moves(grid, R, C)

        if known_safe:
            target = next(iter(known_safe))
            print(f"Logic Deduction: Cell {target} is SAFE. Revealing...")
            play_move("reveal", target[0], target[1])

        elif known_mines:
            target = next(iter(known_mines))
            print(f"Logic Deduction: Cell {target} is a MINE. Flagging...")
            play_move("flag", target[0], target[1])

        else:
            target = get_safest_guess(grid, R, C)
            print(f"Logical Deadlock! Safest Guess chosen: {target}. Revealing with caution...")
            play_move("reveal", target[0], target[1])

        time.sleep(0.4)
