def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    targets = observation.get("unclaimed_cells")
    if not targets:
        targets = observation.get("resources") or []

    best = None
    best_sc = -10**18

    # Deterministic ordering tie-breaker: sort by (x,y)
    if targets:
        tmp = []
        for p in targets:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if ok(x, y):
                    tmp.append((x, y))
        tmp.sort()
        targets = tmp

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    for x, y in (targets if targets else [(w // 2, h // 2)]):
        d_us = man(sx, sy, x, y)
        d_opp = man(ox, oy, x, y)
        edge = 1 if (x == 0 or y == 0 or x == w - 1 or y == h - 1) else 0
        sc = (d_opp - d_us) + 0.3 * edge * (w + h) - 0.02 * d_us
        if sc > best_sc:
            best_sc = sc
            best = (x, y)

    tx, ty = best if best else (w // 2, h // 2)
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Try a small set of deterministic moves that move closer to target and are valid.
    moves = []
    # Prefer primary axis first for determinism
    if dx != 0:
        moves.append((dx, 0))
    if dy != 0:
        moves.append((0, dy))
    moves.append((dx, dy))
    moves.append((0, 0))
    # Remaining small adjustments
    for a in (-1, 0, 1):
        for b in (-1, 0, 1):
            if (a, b) != (0, 0) and (a, b) not in moves and (a, b) != (dx, dy) and (a, b) != (dx, 0) and (a, b) != (0, dy):
                moves.append((a, b))

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if ok(nx, ny):
            return [int(mx), int(my)]
    return [0, 0]