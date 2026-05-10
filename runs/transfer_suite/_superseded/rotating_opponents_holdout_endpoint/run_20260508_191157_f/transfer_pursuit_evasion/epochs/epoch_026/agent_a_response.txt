def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("flee" in role) or ("escape" in role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    def min_obs_dist(x, y):
        if not obstacles:
            return 10**6
        m = 10**6
        for px, py in obstacles:
            d = abs(x - px) + abs(y - py)
            if d < m:
                m = d
        return m

    # Bias direction toward a corner farthest from opponent (for evader), nearest (for pursuer)
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        tx, ty = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    best = None  # (primary, secondary, tie, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = cheb(nx, ny)
        od = min_obs_dist(nx, ny)

        # Deterministic "wall-run" bias: keep moving along the intended corner direction
        # Use dot with (tx-sx, ty-sy), but do not overtake obstacle/cheb objective.
        bias = (1 if (tx - nx) == 0 else 0) + (1 if (ty - ny) == 0 else 0)
        corner_dir_dx = 0 if tx == sx else (1 if tx > sx else -1)
        corner_dir_dy = 0 if ty == sy else (1 if ty > sy else -1)
        dot = dx * corner_dir_dx + dy * corner_dir_dy

        if is_evader:
            primary = d
            secondary = od
            # Prefer increasing corner-aligned progress; tie-break by smallest dot deficit
            tie = dot + bias
        else:
            primary = -d
            secondary = od
            tie = dot + bias

        cand = (primary, secondary, tie, dx, dy)
        if best is None or cand > best:
            best = cand

    return [best[3], best[4]]