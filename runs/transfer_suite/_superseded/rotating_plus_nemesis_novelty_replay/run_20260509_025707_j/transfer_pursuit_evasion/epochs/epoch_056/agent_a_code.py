def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_evader(role):
        r = (role or "").lower()
        return ("evader" in r) or ("runner" in r) or ("evasion" in r) or ("evasive" in r)

    self_evade = is_evader(observation.get("self_role"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def dist(a, b, c, d):
        return max(abs(a - c), abs(b - d))  # Chebyshev works well for 8-way moves

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if self_evade:
            key = (dist(nx, ny, ox, oy), -(abs(nx - (w - 1)) + abs(ny - (h - 1)) + 1e-6), (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
            # maximize distance from pursuer; secondarily prefer escaping corner farthest (deterministic via tie-break)
            key = (-key[0], key[1], key[2])
        else:
            key = (dist(nx, ny, ox, oy), (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]