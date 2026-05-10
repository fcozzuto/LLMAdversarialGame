def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    ob = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "pursuer").lower()
    is_evader = "evader" in role

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def step_ok(x, y):
        return in_bounds(x, y) and (x, y) not in ob

    def manh(x, y):
        return abs(x - ox) + abs(y - oy)

    def mobility(x, y):
        m = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if step_ok(nx, ny):
                m += 1
        return m

    def opp_bias(x, y):
        # Slightly prefer moving toward/away while discouraging staying put.
        d = manh(x, y)
        return d + (0 if (x != sx or y != sy) else 2)

    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not step_ok(nx, ny):
            continue
        d = manh(nx, ny)
        mob = mobility(nx, ny)
        # For pursuer: minimize distance; for evader: maximize distance.
        primary = d if not is_evader else -d
        # Prefer having options; if tied, prefer moving diagonally (often breaks zigzags).
        diag = 0 if (dx == 0 or dy == 0) else 1
        key = (
            primary,
            -mob if not is_evader else mob,
            -diag,
            opp_bias(nx, ny) if not is_evader else -opp_bias(nx, ny),
            dx, dy
        )
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]