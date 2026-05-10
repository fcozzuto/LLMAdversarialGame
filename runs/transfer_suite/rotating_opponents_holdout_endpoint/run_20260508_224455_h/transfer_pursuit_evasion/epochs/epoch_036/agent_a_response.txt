def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    role = str(observation.get("self_role") or "").lower()
    is_evader = any(k in role for k in ("evader", "evade", "runner", "escape"))
    if not role:
        is_evader = True

    def nearest_obs_dist(x, y):
        best = 10**9
        for (a, b) in obs:
            d = abs(x - a) + abs(y - b)
            if d < best:
                best = d
        return best if best != 10**9 else 100

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if nx == ox and ny == oy:
            continue  # avoid immediate capture/being caught when possible

        dist = abs(nx - ox) + abs(ny - oy)
        no_dist = nearest_obs_dist(nx, ny)

        if is_evader:
            val = (dist * 100) + no_dist
        else:
            val = (-dist * 100) + no_dist  # still prefer safer squares if tying

        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val
        elif val == best_val:
            if best is None or (dx, dy) < best:
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]