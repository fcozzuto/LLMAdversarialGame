def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obst_list = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obst_list)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        # No resources: keep max distance while not getting clipped by obstacles
        moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            d_o = cheb((nx, ny), (ox, oy))
            # Prefer moving away; tie-break lexicographically by destination
            key = (-d_o, nx, ny)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    # Pick a resource where we are relatively closer than the opponent (maximize opd - myd)
    best_res = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = cheb((sx, sy), (rx, ry))
        opd = cheb((ox, oy), (rx, ry))
        key = (opd - myd, -myd, -rx, -ry)  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res if best_res is not None else (sx, sy)

    d_o_now = cheb((sx, sy), (ox, oy))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    best_score = None

    # If opponent is very near, prioritize escaping instead of chasing.
    escape_mode = d_o_now <= 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) == (tx, ty):
            # Immediate capture preference
            score = (-10**6, 0, 0, 0)
        else:
            d_t = cheb((nx, ny), (tx, ty))
            d_o = cheb((nx, ny), (ox, oy))
            # Obstacle-aware local pressure: penalize proximity to obstacles
            obs_pressure = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    xx, yy = nx + ax, ny + ay
                    if in_bounds(xx, yy) and (xx, yy) in obstacles:
                        obs_pressure += 1

            if escape_mode:
                # Escape strongly;