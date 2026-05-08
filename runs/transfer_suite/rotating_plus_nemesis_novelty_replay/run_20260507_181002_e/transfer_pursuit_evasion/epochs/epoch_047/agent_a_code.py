def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr)
    if (not self_is_evader) and (("evader" in orr) or ("runner" in orr)):
        self_is_evader = False
    if ("pursuer" in sr) or ("hunter" in sr):
        self_is_evader = False

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    if self_is_evader:
        # maximize distance from pursuer; small preference for staying near center to reduce wall-running traps
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = dist(nx, ny, ox, oy)
            center_pen = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
            score = d * 1000 + center_pen
            if score > best_score:
                best_score, best_move = score, (dx, dy)
    else:
        # minimize distance to evader; tie-break deterministically
        best_score = 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            score = dist(nx, ny, ox, oy)
            if score < best_score:
                best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]