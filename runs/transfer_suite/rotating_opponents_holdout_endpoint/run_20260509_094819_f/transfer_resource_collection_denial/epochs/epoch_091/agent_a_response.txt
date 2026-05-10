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
    moves = sorted(moves, key=lambda t: (t[0], t[1]))  # deterministic tie order

    best = None
    best_move = [0, 0]

    # Evaluate: for each move, pick the resource that maximizes our advantage:
    # (opp_dist - our_dist) primarily, then our_dist, then closer to opponent to deny.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy

        # Find best target for this candidate state.
        cand = None
        for rx, ry in res:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd
            # tie-break: prefer smaller sd (faster pickup), then larger "deny" (our proximity vs their proximity)
            deny = sd - od
            key = (-adv, sd, deny, rx + ry)
            if cand is None or key < cand[0]:
                cand = (key, rx, ry)
        # Primary move score: maximize adv (handled by key), minimize sd, deterministic.
        move_key = cand[0]

        if best is None or move_key < best:
            best = move_key
            best_move = [nx - sx, ny - sy]

    return best_move