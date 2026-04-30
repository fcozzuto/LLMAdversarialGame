def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if p is None:
            continue
        try:
            x, y = p
            obstacles.add((x, y))
        except Exception:
            pass

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    best = (0, 0)
    best_key = None

    if resources:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            # distance-based advantage over opponent, choose move that creates strongest lead on some resource
            min_gap = 10**9
            min_d1 = 10**9
            for rx, ry in resources:
                d1 = md(nx, ny, rx, ry)
                d2 = md(ox, oy, rx, ry)
                gap = d1 - d2  # negative => we are closer
                if gap < min_gap:
                    min_gap = gap
                if d1 < min_d1:
                    min_d1 = d1
            # if we cannot gain advantage (min_gap >= 0), push to reduce our distance and stay farther from opponent
            d_opp = md(nx, ny, ox, oy)
            objective = (min_gap * 100) + (min_d1) + (1 if min_gap < 0 else -2) * d_opp
            key = (objective, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    # No resources: deterministically move to maximize distance from opponent, avoiding obstacles
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_opp = md(nx, ny, ox, oy)
        # tie-break prefers staying still slightly less than moving (deterministic)
        objective = (-d_opp, dx, dy)
        if best_key is None or objective < best_key:
            best_key = objective
            best = (dx, dy)
    return [best[0], best[1]]