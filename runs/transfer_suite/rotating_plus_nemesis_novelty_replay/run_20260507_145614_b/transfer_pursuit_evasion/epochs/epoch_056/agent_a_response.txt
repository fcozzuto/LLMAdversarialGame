def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    srole = (observation.get("self_role") or "").lower()
    orole = (observation.get("opponent_role") or "").lower()
    self_is_evader = ("evader" in srole) or ("evasion" in srole) or ("evader" in orole and "pursuer" in srole)

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    phase = int(observation.get("turn_index", 0) or 0) & 1
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if phase:
        dirs = dirs[5:] + dirs[:5]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def score(x, y):
        dx = x - ox
        dy = y - oy
        d2 = dx*dx + dy*dy
        # Small deterministic nudge to reduce oscillations around obstacles/boundaries
        boundary_pen = 0
        if x == 0 or x == w-1: boundary_pen += 1
        if y == 0 or y == h-1: boundary_pen += 1
        # Evader: maximize distance; Pursuer: minimize distance (greedy)
        return (-d2 if self_is_evader else d2) - (boundary_pen if not self_is_evader else -boundary_pen)

    best_mv = (0, 0)
    best_sc = None
    for d in dirs:
        nx, ny = sx + d[0], sy + d[1]
        if not ok(nx, ny):
            continue
        sc = score(nx, ny)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_mv = d

    return [int(best_mv[0]), int(best_mv[1])]