def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    role = observation.get("self_role", "pursuer")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    best = None
    if role == "pursuer":
        target_corner = min(corners, key=lambda c: dist((ox, oy), c))
        best_sc = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            d_op = dist((nx, ny), (ox, oy))
            d_corner = dist((nx, ny), target_corner)
            sc = -d_op * 20 - d_corner
            # slight tie-breaker: prefer moves that reduce distance to opponent or keep safe
            if sc > best_sc:
                best_sc = sc
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]
    else:
        # Evader: maximize distance from pursuer; also drift toward farthest corner.
        far_corner = max(corners, key=lambda c: dist((sx, sy), c))
        best_sc = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            d_op = dist((nx, ny), (ox, oy))
            d_corner = dist((nx, ny), far_corner)
            sc = d_op * 25 - d_corner
            if sc > best_sc:
                best_sc = sc
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]