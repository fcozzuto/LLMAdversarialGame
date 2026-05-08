def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    i_am_evader = ("evader" in self_role) or ("pursuer" in opponent_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    def risk(x, y):
        if (x, y) in obs:
            return 10**9
        r = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not inb(nx, ny) or (nx, ny) in obs:
                    r += 2
        return r

    def score_cell(x, y):
        d2 = (x - ox) * (x - ox) + (y - oy) * 1 + (0)  # keep deterministic simple
        # actual d2
        d2 = (x - ox) * (x - ox) + (y - oy) * (y - oy)
        r = risk(x, y)
        if i_am_evader:
            # prefer larger distance; avoid corridors and obstacles; avoid moving onto opponent
            return (-d2) + r * 10 + (1 if (x == ox and y == oy) else 0) * 10**6
        else:
            # pursuer: minimize distance; strongly avoid obstacles and avoid staying
            stay_pen = 1 if (x == sx and y == sy) else 0
            return (d2) + r * 10 + stay_pen * 3

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = score_cell(nx, ny)
        if best_val is None or (v < best_val) or (v == best_val and (dx, dy) < best):
            best_val = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]