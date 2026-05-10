def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = observation.get("unclaimed_cells", []) or []
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def center_bias(x, y):
        return abs(x - cx) + abs(y - cy)

    targets = []
    if unclaimed:
        for tx, ty in unclaimed:
            if not inb(tx, ty) or blocked(tx, ty):
                continue
            targets.append((tx, ty))
        if len(targets) > 10:
            targets.sort(key=lambda p: center_bias(p[0], p[1]))
            targets = targets[:10]
    if not targets:
        for tx, ty in opp_terr:
            if inb(tx, ty) and not blocked(tx, ty):
                targets.append((tx, ty))
        if len(targets) > 10:
            targets.sort(key=lambda p: center_bias(p[0], p[1]))
            targets = targets[:10]
    if not targets:
        for tx, ty in self_terr:
            if inb(tx, ty) and not blocked(tx, ty):
                targets.append((tx, ty))
        if not targets:
            targets = [(ox, oy), (sx, sy)]

    def score_cell(x, y):
        d1 = abs(x - sx) + abs(y - sy)
        d2 = abs(x - ox) + abs(y - oy)
        on_unclaimed = (x, y) in set(map(tuple, unclaimed)) if unclaimed else False
        on_opp = (x, y) in opp_terr
        return (-(30 if on_unclaimed else 0) - (20 if on_opp else 0)) + (d1 - 0.25 * d2) + 0.02 * center_bias(x, y)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        # Immediate heuristic: prefer moves that reduce distance to best target.
        if targets:
            val = min(score_cell(nx, ny) - (abs(nx - tx) + abs(ny - ty)) for tx, ty in targets)
        else:
            val = abs(nx - ox) + abs(ny - oy)
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]