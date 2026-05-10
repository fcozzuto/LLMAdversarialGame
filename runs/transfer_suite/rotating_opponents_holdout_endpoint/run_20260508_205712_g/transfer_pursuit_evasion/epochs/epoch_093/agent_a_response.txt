def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in sr) or ("runner" in sr) or ("evasion" in sr)
    if ("pursuer" in sr) or ("chaser" in sr) or ("hunter" in sr):
        is_evader = False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def min_obst_dist2(x, y):
        md = None
        for ax, ay in obstacles:
            d = dist2(x, y, ax, ay)
            if md is None or d < md:
                md = d
        return 999999 if md is None else md

    best_move = [0, 0]
    best_val = None

    if not is_evader:
        # Pursuer: minimize distance to opponent; prefer moves that stay away from obstacles.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            obst = min_obst_dist2(nx, ny)
            # Strong weight on distance to ensure pursuit; mild tie-break for obstacle safety.
            val = d * 10 - obst
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        # Evader: maximize distance from pursuer; avoid obstacles and walls indirectly.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            obst = min_obst_dist2(nx, ny)
            # Prefer staying far and not getting too close to obstacles; slight preference for diagonal/wall freedom.
            wall_pen = 0
            if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
                wall_pen = 1
            val = -(d * 10 + obst * 2) + wall_pen * 3
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move