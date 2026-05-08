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

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr) or (("pursuer" not in sr) and ("evader" in orr))

    moves = [(0, 0), (1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    if self_is_evader:
        target = max(corners, key=lambda c: (md(c[0], c[1], ox, oy), -c[0], -c[1]))
    else:
        target = (ox, oy)

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        if self_is_evader:
            key = (md(nx, ny, ox, oy), md(nx, ny, target[0], target[1]), nx, ny)
            # maximize distance from pursuer; deterministic tie-break favors larger md then larger corner distance
            key = (key[0], key[1], key[2], key[3])
        else:
            # minimize distance to opponent; deterministic tie-break favors smaller distance then toward top-left
            key = (-md(nx, ny, target[0], target[1]), -md(nx, ny, ox, oy), -nx, -ny)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]