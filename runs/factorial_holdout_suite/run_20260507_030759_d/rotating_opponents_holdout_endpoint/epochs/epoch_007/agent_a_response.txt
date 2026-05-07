def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def man(a, b, c, d): return abs(a - c) + abs(b - d)
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        lead = od - sd  # higher means we are closer
        # prioritize: take resources we can reach first (lead), then closer, then keep away from opponent
        key = (-lead, sd, -od, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), sd, od)

    if best is None:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: man(ox, oy, c[0], c[1]) - man(sx, sy, c[0], c[1]))
    else:
        _, (tx, ty), _, _ = best

    # If opponent is already adjacent to us, slightly prioritize increasing distance
    opp_adj = (abs(sx - ox) <= 1 and abs(sy - oy) <= 1)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            ds = man(nx, ny, tx, ty)
            dopt = man(nx, ny, ox, oy)
            # discourage moves that let opponent immediately grab nearby resources
            near_opp = 1 if dopt <= 2 else 0
            # encourage diagonal-ish progress only via ds (man handles)
            score = ds * 10 + near_opp * 6 - dopt
            if opp_adj:
                score += -dopt * 2  # increase distance from opponent when too close
            candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][1]), int(candidates[0][2])]