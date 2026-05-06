def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Prefer moves that secure a resource sooner than the opponent, and avoid moving into tight opponent races.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # Compute best advantage across resources
        # Score: higher is better. Large penalty if opponent reaches some resource significantly earlier.
        local_best_adv = -10**9
        local_best_t = 10**9
        worst_race_pen = 0
        for rx, ry in resources:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer than opponent
            if adv > local_best_adv:
                local_best_adv = adv
            if ds < local_best_t:
                local_best_t = ds
            # If we lag behind by at least 1, penalize more when very close to opponent
            lag = ds - do
            if lag >= 1:
                worst_race_pen += lag * lag

        # Tie-break: prefer shorter self distance and slightly prefer moving away from opponent when racing is lost.
        dist_opp_here = md(nx, ny, ox, oy)
        base = local_best_adv * 10 - local_best_t - worst_race_pen * 2 + dist_opp_here * 0.2
        cand = base

        if best_score is None or cand > best_score or (cand == best_score and (dx, dy) < best):
            best_score = cand
            best = (dx, dy)

    return [int(best[0]), int(best[1])]