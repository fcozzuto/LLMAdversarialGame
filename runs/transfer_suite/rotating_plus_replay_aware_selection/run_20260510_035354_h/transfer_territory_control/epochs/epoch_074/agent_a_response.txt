def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []
    opp_terr = observation.get("opponent_territory") or []

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    obset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Candidate targets: prefer unclaimed, but include opponent territory if unclaimed scarce
    targets = [(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2]
    if len(targets) < 6:
        targets += [(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2]

    if not targets:
        return [0, 0]

    # Score: closer to center and closer to us; slightly prefer cells that are not obstacles
    best_t = None
    best_s = -10**18
    for (tx, ty) in targets:
        if (tx, ty) in obset:
            continue
        d_us = man(ax, ay, tx, ty)
        d_cent = abs(tx - cx) + abs(ty - cy)
        # Higher is better
        s = (-d_us) + (-0.8 * d_cent)
        if s > best_s:
            best_s = s
            best_t = (tx, ty)

    tx, ty = best_t
    def step_toward(x, y, tx, ty):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        return dx, dy

    dx, dy = step_toward(ax, ay, tx, ty)
    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == 0 and my == 0:
                pass
            nx, ny = ax + mx, ay + my
            if not inb(nx, ny) or (nx, ny) in obset:
                continue
            # Evaluate immediate move toward target and center
            d_us = man(nx, ny, tx, ty)
            d_cent = abs(nx - cx) + abs(ny - cy)
            # Prefer reducing distance to target; tie-break toward center
            score = (-d_us) + (-0.5 * d_cent)
            candidates.append((score, mx, my))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, bx, by = candidates[0]
    return [int(bx), int(by)]