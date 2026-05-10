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

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("escape" in role) or ("runner" in role) or ("evader" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18 if is_evader else 10**18

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def obs_pen(x, y):
        if not obstacles:
            return 0
        m = 10**9
        for a, b in obstacles:
            d = abs(x - a) + abs(y - b)
            if d < m:
                m = d
        return 0 if m == 10**9 else m

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d2 = dist2(nx, ny, ox, oy)
        o = obs_pen(nx, ny)
        # Evader: maximize distance and keep away from obstacles.
        # Pursuer: minimize distance and allow moving toward opponent while staying clear.
        val = (d2 + 0.35 * o) if is_evader else (-d2 + 0.20 * o)
        if (is_evader and val > best_val) or ((not is_evader) and val < best_val):
            best_val = val
            best_move = [dx, dy]

    # If all moves were invalid (rare), fall back to staying put.
    return best_move