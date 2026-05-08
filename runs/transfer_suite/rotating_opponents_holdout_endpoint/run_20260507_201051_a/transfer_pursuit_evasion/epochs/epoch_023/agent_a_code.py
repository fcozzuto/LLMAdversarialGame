def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("chase" in role) or ("pursuer" in role)

    if is_pursuer:
        tx = max(0, min(w - 1, 2 * ox - sx))
        ty = max(0, min(h - 1, 2 * oy - sy))
    else:
        tx, ty = ox, oy

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_tar = abs(nx - tx) + abs(ny - ty)
        # Avoid stepping onto/adjacent to obstacles only lightly to reduce cornering failures.
        adj_obs = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                xx, yy = nx + ddx, ny + ddy
                if (xx, yy) in obs:
                    adj_obs += 1
        # Score: pursuer minimizes distance to opponent/intercept; evader maximizes distance.
        if is_pursuer:
            val = (d_opp * 100 + d_tar * 2 + adj_obs * 5)
            better = (best_val is None) or (val < best_val)
        else:
            val = (-(d_opp * 100 + d_tar * 2) + adj_obs * 5)
            better = (best_val is None) or (val < best_val)

        if better:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]