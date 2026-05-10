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

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    pursuit = ("purs" in self_role) or (not ("evad" in self_role) and ("purs" in opponent_role or "purs" in self_role))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def free_neighbors(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    c += 1
        return c

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx * ddx + ddy * ddy
        mob = free_neighbors(nx, ny)
        center_pref = -((nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2) / (w * h)
        # If pursuing: prefer smaller distance, and also reduce our mobility only slightly (avoid traps).
        # If evading: prefer larger distance, and increase our mobility; try to corner opponent by moving toward their nearest wall.
        if pursuit:
            score = dist2 + (0.25 / (1 + mob)) + 0.02 * (-center_pref)
            # Make diagonal less likely when it would land on low-mobility squares (zigzag evader)
            if dx != 0 and dy != 0:
                score += 0.15 / (1 + mob)
        else:
            score = -dist2 + (-0.12 * mob) + 0.01 * (center_pref)
            if dx != 0 and dy != 0:
                score += 0.08 * (1 / (1 + mob))
        candidates.append((score, dx, dy))

    # Deterministic tie-breaker: smallest score then prefer moves that change x, then y, then diagonal, then stay.
    # (Since engine rejects invalid moves by keeping place, staying is always valid if listed; here it's filtered by obstacles.)
    best = None
    for score, dx, dy in candidates:
        key = (score, abs(dx), abs(dy), 0 if (dx != 0 and dy != 0) else 1, 0 if (dx == 0 and dy == 0) else 1)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1] if best is not None else [0, 0]