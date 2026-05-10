def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    evade = ("evad" in role) or ("evad" in opp_role and "purs" not in role)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d = abs(nx - ox) + abs(ny - oy)
        # Avoid getting stuck on/near obstacles: small penalty if close to any obstacle.
        close_obs = 0
        for ax, ay in obs:
            if abs(nx - ax) + abs(ny - ay) == 1:
                close_obs += 1

        corner_dist = min(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)

        if evade:
            # Maximize distance; prefer moving toward the farthest corner; reduce obstacle proximity.
            key = (d, corner_dist, -close_obs, dx * dx + dy * dy)
        else:
            # Minimize distance to capture; prefer moving toward the nearest corner (can reduce evasion space);
            # reduce obstacle proximity. Also prefer diagonal when it helps.
            key = (-d, -corner_dist, -close_obs, dx * dx + dy * dy)

        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best