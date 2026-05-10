def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None  # (cost, mydist, i)
    for i, (rx, ry) in enumerate(resources):
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        row_bonus = 1.2 if ry == oy else 0.0  # likely sweep_rows pressure
        col_bonus = 0.6 if rx == ox else 0.0
        # Lower cost is better: want sd small and od large; prefer same-row/col denial.
        cost = sd - 1.15 * od - row_bonus - col_bonus
        cand = (cost, sd, i)
        if best is None or cand < best:
            best = cand

    i = best[2]
    tx, ty = resources[i]
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    pref = []
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not in_bounds(nx, ny):
            continue
        # Prefer moves that reduce distance to target; slightly avoid letting opponent get closer.
        d_self = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)
        pref.append((d_self, -d_opp, mx, my))
    if not pref:
        return [0, 0]
    pref.sort()
    return [int(pref[0][2]), int(pref[0][3])]