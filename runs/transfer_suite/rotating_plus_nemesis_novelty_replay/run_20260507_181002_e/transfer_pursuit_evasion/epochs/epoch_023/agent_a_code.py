def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    srole = str(observation.get("self_role", "")).lower()
    orole = str(observation.get("opponent_role", "")).lower()

    i_am_pursuer = ("pursuer" in srole) or ("chaser" in srole) or ("catch" in srole) or ("pursuit" in srole)
    if "evader" in srole or "evad" in srole: i_am_pursuer = False
    if ("pursuer" in orole) or ("chaser" in orole) or ("catch" in orole) or ("pursuit" in orole): i_am_pursuer = False

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cand.append((dx, dy))

    if not cand:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def manhattan(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        md = manhattan(nx, ny, ox, oy)
        ed = dist2(nx, ny, ox, oy)
        cen = dist2(nx, ny, cx, cy)
        diag_bonus = 1 if (dx != 0 and dy != 0) else 0
        # Pursuer: minimize manhattan, then euclid; also slightly prefer diagonals and keep central.
        # Evader: maximize manhattan, then euclid; also slightly prefer diagonals and keep away from center.
        if i_am_pursuer:
            key = (md, ed, -diag_bonus, cen)
        else:
            key = (-md, -ed, -diag_bonus, -cen)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1]