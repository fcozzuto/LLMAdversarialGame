def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h:
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def nearest_res_dist(x, y):
        if not resources:
            return 0
        best = None
        for rx, ry in resources:
            d = abs(x - rx) + abs(y - ry)
            if best is None or d < best:
                best = d
        return best if best is not None else 0

    best_move = [0, 0]
    best_key = None
    # deterministic tie-break order by move list order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        if obs:
            d_obs = min(abs(nx - ax) + abs(ny - ay) for ax, ay in obs)
        else:
            d_obs = 10**6
        d_res = nearest_res_dist(nx, ny)

        if is_evader:
            # flee opponent, avoid obstacles, also drift toward resources if any (small weight)
            key = (d_opp, d_obs, -d_res, dx, dy)
        else:
            # chase opponent while staying away from obstacles; prefer resources
            key = (-d_opp, -d_obs, d_res, dx, dy)

        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    if not best_key:
        return [0, 0]
    return best_move