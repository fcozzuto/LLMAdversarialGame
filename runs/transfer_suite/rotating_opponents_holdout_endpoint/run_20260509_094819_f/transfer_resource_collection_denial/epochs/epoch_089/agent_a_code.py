def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy  # engine would keep us in place on invalid moves

        self_d_opp = md(nx, ny, ox, oy)
        # Evaluate the best resource we can aim for after this move
        best_adv = None
        best_self_d = None
        best_target = None
        for tx, ty in res:
            sd = md(nx, ny, tx, ty)
            od = md(ox, oy, tx, ty)
            adv = od - sd  # positive means we are closer than opponent
            if best_adv is None or adv > best_adv or (adv == best_adv and (best_self_d is None or sd < best_self_d)) or (adv == best_adv and sd == best_self_d and (best_target is None or (tx, ty) < best_target)):
                best_adv = adv
                best_self_d = sd
                best_target = (tx, ty)

        # If opponent can grab "best" target sooner, avoid helping them: prefer moves that keep opponent farther
        # Small penalty based on closeness to opponent to avoid oscillating into their path.
        opp_penalty = 0.02 * self_d_opp
        val = best_adv - opp_penalty

        # If we land on a resource, strongly commit to immediate capture
        if (nx, ny) in res:
            val += 10.0

        # Prefer higher val, then smaller distance to that chosen target, then deterministic tie-break
        key = (-val, best_self_d if best_self_d is not None else 0, best_target[0], best_target[1], dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx if (sx + dx == nx) else 0, dy if (sy + dy == ny) else 0])

    return best[1] if best is not None else [0, 0]