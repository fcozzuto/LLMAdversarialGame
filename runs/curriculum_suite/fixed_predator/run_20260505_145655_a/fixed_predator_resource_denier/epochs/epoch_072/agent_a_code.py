def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = (-1, 0, 1)
    legal = []
    for dx in dirs:
        for dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best_move = (0, 0, -10**18, 10**9)  # dx,dy,val,sd
    for dx, dy, nx, ny in legal:
        best_val = -10**18
        best_sd = 10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer taking resources we beat; if not, go for ones that are urgent/close for us while denying.
            val = (od - sd) * 35 - sd
            val += 8 if od - sd >= 3 else 0
            val -= 15 if od - sd < 0 else 0
            if val > best_val or (val == best_val and sd < best_sd):
                best_val, best_sd = val, sd
        if best_val > best_move[2] or (best_val == best_move[2] and best_sd < best_move[3]):
            best_move = (dx, dy, best_val, best_sd)

    return [int(best_move[0]), int(best_move[1])]