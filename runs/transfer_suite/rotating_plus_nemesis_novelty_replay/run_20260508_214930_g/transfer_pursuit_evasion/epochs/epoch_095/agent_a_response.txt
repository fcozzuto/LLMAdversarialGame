def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "fugitive"))
    if not is_evader:
        is_pursuer = True
    else:
        is_pursuer = False

    obs_list = observation.get("obstacles") or []
    obs = set()
    for b in obs_list:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs

    # evasion_corner style: head to farthest corner, but avoid obstacles by preferring clear moves
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    def score_move(nx, ny):
        if blocked(nx, ny):
            return -10**9
        if is_pursuer:
            # pursue: minimize distance to opponent, with obstacle proximity penalty
            d = max(abs(nx - ox) + abs(ny - oy), 0)
            prox = 0
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (nx + dx, ny + dy) in obs:
                    prox += 1
            # slight preference for not drifting away from opponent when tied
            drift = (abs(nx - sx) + abs(ny - sy)) * 0.01
            return -d - 0.4 * prox - drift
        else:
            # evader: maximize distance to opponent while moving toward far_corner
            d = abs(nx - ox) + abs(ny - oy)
            toward = abs(nx - far_corner[0]) + abs(ny - far_corner[1])
            prox = 0
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (nx + dx, ny + dy) in obs:
                    prox += 1
            return d * 1.0 - toward * 0.6 - 0.4 * prox

    best = None
    best_s = -10**18
    # deterministic tie-breaker: lexicographic by dx,dy as given by deltas ordering
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        s = score_move(nx, ny)
        if s > best_s:
            best_s = s
            best = (dx, dy)

    if best is None:
        # fallback: try staying
        if in_bounds(sx, sy) and not blocked(sx, sy):
            return [0, 0]
        # otherwise choose any legal in-bounds non-blocked move deterministically
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and not blocked(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]