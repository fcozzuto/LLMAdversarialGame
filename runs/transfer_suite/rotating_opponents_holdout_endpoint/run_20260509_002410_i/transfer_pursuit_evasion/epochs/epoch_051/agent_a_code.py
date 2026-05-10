def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in self_role) or (self_role == "pursuer")
    # If unclear, default to pursuer-like (slightly safer against most pools).
    if not ("evader" in self_role or self_role == "evader") and not is_pursuer:
        is_pursuer = True

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def obs_pen(x, y):
        if (x, y) in obstacles:
            return 10**9
        pen = 0
        for (ox2, oy2) in obstacles:
            md = abs(x - ox2) + abs(y - oy2)
            if md == 0:
                return 10**9
            if md == 1:
                pen += 5
            elif md == 2:
                pen += 2
        return pen

    def score_for(x, y):
        d2 = (x - ox) * (x - ox) + (y - oy) * (y - oy)
        pen = obs_pen(x, y)
        if pen >= 10**8:
            return -10**18 if is_pursuer else 10**18
        if is_pursuer:
            # Prefer capture, then minimize distance; also avoid obstacles.
            cap = 10**12 if (x == ox and y == oy) else 0
            corner = (x == 0 or x == w - 1) and (y == 0 or y == h - 1)
            return cap + (-d2) * 10 + (-pen) * 5 + (1 if corner else 0)
        else:
            # Evader: maximize distance; slightly prefer staying away from obstacles and edging to corners.
            corner = (x == 0 or x == w - 1) and (y == 0 or y == h - 1)
            return (d2) * 10 + (-pen) * 5 + (1 if corner else 0)

    best = None
    best_move = [0, 0]
    # Deterministic tie-break: lower dx, then lower dy via sorted scan order above already fixed.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score_for(nx, ny)
        if best is None or (sc > best):
            best = sc
            best_move = [dx, dy]

    return best_move