def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    res_set = set((r[0], r[1]) for r in resources)
    best_r = None
    best_r_score = None
    for rx, ry in resources:
        if (rx, ry) in obstacles or not inb(rx, ry):
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer resources where we are closer; if tie, prefer ones we can arrive soon.
        sc = (od - sd) * 1000 - sd
        if best_r_score is None or sc > best_r_score:
            best_r_score = sc
            best_r = (rx, ry)

    if best_r is None:
        tx, ty = ox, oy
    else:
        tx, ty = best_r

    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        nd_self = man(nx, ny, tx, ty)
        nd_opp = man(ox, oy, tx, ty)
        # If we land on any resource, strongly prefer it.
        land_bonus = 2000 if (nx, ny) in res_set else 0

        # Also encourage moves that reduce our distance while not making us much worse relative to the opponent.
        sc = land_bonus + (nd_opp - nd_self) * 10 - nd_self

        # Tiny deterministic tiebreak to avoid oscillation.
        sc += - (dx * 3 + dy)

        if best_score is None or sc > best_score:
            best_score = sc
            best_move = [dx, dy]

    return best_move