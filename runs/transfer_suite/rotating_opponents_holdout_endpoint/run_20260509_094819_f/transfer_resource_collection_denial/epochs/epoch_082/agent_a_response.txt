def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_step_toward(tx, ty):
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obs:
                continue
            self_d = abs(nx - tx) + abs(ny - ty)
            opp_d = abs(nx - ox) + abs(ny - oy)
            opp_here = abs(sx - ox) + abs(sy - oy)
            adv = (abs(tx - ox) + abs(ty - oy)) - self_d
            # Prefer moves that reduce distance to the target and keep/extend advantage
            score = 2.5 * adv - 0.35 * self_d + 0.10 * (opp_here - opp_d) - 0.02 * (nx == tx and ny == ty)
            if best is None or score > best[0] or (score == best[0] and (nx, ny) < best[1]):
                best = (score, (nx, ny), dx, dy)
        return [best[2], best[3]] if best is not None else [0, 0]

    if not res:
        return [0, 0]

    # Pick the resource with maximum "reach advantage", tie-break deterministically by position
    best_target = None
    for t in res:
        sd = abs(t[0] - sx) + abs(t[1] - sy)
        od = abs(t[0] - ox) + abs(t[1] - oy)
        adv = od - sd  # positive means we are closer/equal
        # Encourage closer targets too
        score = 3.0 * adv - 0.10 * sd
        if best_target is None or score > best_target[0] or (score == best_target[0] and t < best_target[1]):
            best_target = (score, t)

    tx, ty = best_target[1]
    return best_step_toward(tx, ty)