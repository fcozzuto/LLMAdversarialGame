def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in v or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    oppT = toset(observation.get("opponent_territory"))
    selfT = toset(observation.get("self_territory"))
    candidates = list(unclaimed) if unclaimed else (list(oppT) if oppT else list(selfT))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    dirs = {(0, 0): 0, (1, 0): 1, (-1, 0): 2, (0, 1): 3, (0, -1): 4, (1, 1): 5, (1, -1): 6, (-1, 1): 7, (-1, -1): 8}

    if not candidates:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def score_cell(x, y):
        d1 = abs(sx - x) + abs(sy - y)
        dO = abs(ox - x) + abs(oy - y)
        center = abs(x - cx) + abs(y - cy)
        # Prefer grabbing unclaimed: boost toward center slightly, and keep away from opponent
        base = d1
        if (x, y) in unclaimed:
            return base - 0.35 * dO + 0.12 * center - 0.02 * (abs(sx - x) != 0 and abs(sy - y) != 0)
        # If no unclaimed: try to invade if it increases distance from opponent line
        return base - 0.25 * dO + 0.25 * center

    best = None
    best_sc = None
    for x, y in candidates:
        sc = score_cell(x, y)
        if best_sc is None or sc < best_sc or (sc == best_sc and (x, y) < best):
            best_sc, best = sc, (x, y)

    tx, ty = best
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy, abs(nx - tx) + abs(ny - ty), dirs[(dx, dy)]))
    if not valid:
        return [0, 0]
    valid.sort(key=lambda t: (t[2], t[3]))
    return [int(valid[0][0]), int(valid[0][1])]