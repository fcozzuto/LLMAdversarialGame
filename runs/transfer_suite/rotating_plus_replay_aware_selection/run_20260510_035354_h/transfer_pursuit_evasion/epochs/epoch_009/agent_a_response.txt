def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()

    is_pursuer = False
    if "purs" in self_role:
        is_pursuer = True
    elif "evad" in self_role:
        is_pursuer = False
    else:
        if "purs" in opponent_role and "evad" not in self_role:
            is_pursuer = False

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = md(nx, ny, ox, oy)
        # Small deterministic tie-break: prefer moves that keep within bounds and avoid staying if possible
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        if is_pursuer:
            # maximize chance to capture: primary minimize distance, secondary reduce stay, then lexicographic by (dx,dy)
            key = (d, stay_pen, dx, dy)
        else:
            # maximize survival: primary maximize distance, secondary reduce stay
            key = (-d, stay_pen, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [best[0], best[1]]