def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    role = observation.get("self_role", "pursuer")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Candidate deltas (including stay)
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if role == "pursuer":
        # Chase while also biasing toward cutting off toward the closest evasion corner.
        target_corner = min(corners, key=lambda c: dist((ox, oy), c))
        best = None
        best_sc = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            d_op = dist((nx, ny), (ox, oy))
            # If we're closer to target corner, it's likely to intercept.
            d_corner = dist((nx, ny), target_corner)
            sc = -d_op * 10 - d_corner
            if sc > best_sc:
                best_sc = sc
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Evader: maximize distance to pursuer, with obstacle-aware move selection and corner preference.
    best = None
    best_sc = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        d_op = dist((nx, ny), (ox, oy))
        # Prefer moves that also head toward the farthest corner from opponent.
        far_corner = max(corners, key=lambda c: dist((ox, oy), c))
        d_corner = dist((nx, ny), far_corner)
        # Mildly avoid moving adjacent to obstacle clusters.
        near_obs = 0
        for ex, ey in obstacles:
            if abs(ex - nx) <= 1 and abs(ey - ny) <= 1:
                near_obs += 1
        sc = d_op * 10 - d_corner - near_obs * 2
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)
    return [best[0], best[1]] if best is not None else [0, 0]