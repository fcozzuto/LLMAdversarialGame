def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        if (sx + dx, sy + dy) in obstacles or not (0 <= sx + dx < w and 0 <= sy + dy < h):
            opts = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
            for ddx, ddy in opts:
                nx, ny = sx + ddx, sy + ddy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    return [ddx, ddy]
        return [dx, dy]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cell_pref(x, y):
        # Prefer resources closer to "diagonal" midline and lower x then y (deterministic)
        return -abs((x - (w - 1) / 2) - (y - (h - 1) / 2))

    me = (sx, sy)
    opp = (ox, oy)

    best = None
    best_key = None
    for rx, ry in resources:
        sd = dist(me, (rx, ry))
        od = dist(opp, (rx, ry))
        # Maximize advantage; then prefer closer to self; then deterministic bias
        key = (od - sd, -sd, cell_pref(rx, ry), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx0 = 0 if sx == tx else (1 if sx < tx else -1)
    dy0 = 0 if sy == ty else (1 if sy < ty else -1)

    # Diagonal first, then cardinal, then stay; deterministic obstacle avoidance
    candidates = []
    if dx0 != 0 and dy0 != 0:
        candidates.append((dx0, dy0))
    candidates.append((dx0, 0) if dx0 != 0 else (0, 0))
    candidates.append((0, dy0) if dy0 != 0 else (0, 0))
    candidates.append((0, 0))
    # Remove duplicates while preserving order
    seen = set()
    ordered = []
    for ddx, ddy in candidates:
        if (ddx, ddy) not in seen:
            seen.add((ddx, ddy))
            ordered.append((ddx, ddy))

    for ddx, ddy in ordered:
        nx, ny = sx + ddx, sy + ddy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(ddx), int(ddy)]

    # Fallback: deterministic scan of all moves
    for ddx in (-1, 0, 1):
        for ddy in (-1, 0, 1):
            nx, ny = sx + ddx, sy + ddy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [int(ddx), int(ddy)]
    return [0, 0]