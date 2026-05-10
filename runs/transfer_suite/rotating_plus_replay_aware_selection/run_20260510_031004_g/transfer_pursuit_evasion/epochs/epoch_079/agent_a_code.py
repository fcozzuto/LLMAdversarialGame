def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("evad" in opp_role and "purs" not in self_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        valid = inb(nx, ny) and (nx, ny) not in obstacles
        if not valid:
            nx, ny = sx, sy

        d2 = dist2(nx, ny, ox, oy)

        # Small anticipatory bias for zigzag: favor aligning movement direction toward opponent.
        step_toward = (1 if ox > sx else (-1 if ox < sx else 0), 1 if oy > sy else (-1 if oy < sy else 0))
        align = 0
        if valid:
            align = (1 if dx == step_toward[0] else 0) + (1 if dy == step_toward[1] else 0)

        # Obstacle proximity penalty to avoid getting trapped.
        prox_pen = 0
        if valid:
            for ax, ay in obstacles:
                dd = dist2(nx, ny, ax, ay)
                if dd <= 4:  # within Chebyshev ~2
                    prox_pen += 2

        # Deterministic tie-break: prefer moves that reduce/enhance manhattan and then fixed dir order.
        man = abs(nx - ox) + abs(ny - oy)
        base = (1000000 if (not valid) else 0) + prox_pen + (0 if is_pursuer else 0)

        # Pursuer wants minimize distance; evader wants maximize.
        if is_pursuer:
            val = d2 + man * 0.2 - align * 0.5 + base
            better = (best is None) or (val < best_val) or (val == best_val and (dx, dy) < best)
        else:
            val = -d2 + man * -0.2 + prox_pen - align * 0.5 + base
            better = (best is None) or (val > best_val) or (val == best_val and (dx, dy) < best)
        if better:
            best = (dx, dy)
            best_val = val

    return [best[0], best[1]]