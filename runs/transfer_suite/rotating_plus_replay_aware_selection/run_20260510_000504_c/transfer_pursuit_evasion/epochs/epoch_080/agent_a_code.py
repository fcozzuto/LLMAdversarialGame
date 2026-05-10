def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or ("flee" in self_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    t = int(observation.get("turn_index", 0) or 0)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def obstacle_pressure(x, y):
        # Penalize moving into tighter areas near obstacles to reduce being blocked.
        neigh = ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1), (x - 1, y - 1), (x + 1, y + 1), (x - 1, y + 1), (x + 1, y - 1))
        c = 0
        for nx, ny in neigh:
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obstacles:
                c += 1
        return c

    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        d = dist2(nx, ny)
        press = obstacle_pressure(nx, ny)

        # Evader wants larger distance; pursuer wants smaller distance.
        # Also add small preference to avoid crowded obstacle-adjacent squares.
        if is_evader:
            val = (d * 4) - press * 2
        else:
            val = (-d * 4) - press * 2

        # Deterministic tie-break: prefer lexicographically smaller move with phase-based parity.
        tie = ((nx + ny + t) & 3) - 1  # {-1,0,1,2} but deterministic
        if best_val is None or val > best_val or (val == best_val and tie > best_tie) or (val == best_val and tie == best_tie and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_tie = tie
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]