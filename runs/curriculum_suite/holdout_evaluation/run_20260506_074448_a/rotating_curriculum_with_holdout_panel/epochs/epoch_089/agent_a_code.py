def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    resources = observation.get("resources") or []

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def legal(dx, dy):
        nx, ny = sx + dx, sy + dy
        return inb(nx, ny) and (nx, ny) not in obstacles

    # Fallback: move toward center if no resources visible
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = (-10**18, 0, 0)
        for dx, dy in deltas:
            if not legal(dx, dy):
                continue
            nx, ny = sx + dx, sy + dy
            # Prefer getting closer to center, deterministic tie-break by deltas order
            val = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
            if val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]] if best[0] > -10**17 else [0, 0]

    best = (-10**18, 0, 0)
    # Heuristic: maximize advantage over opponent on the best available resource
    for dx, dy in deltas:
        if not legal(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy

        # Choose resource that gives maximal immediate strategic advantage
        local_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = d2(nx, ny, rx, ry)
            od = d2(ox, oy, rx, ry)
            # Prefer making opponent farther while also approaching our chosen resource
            # Advantage: od - sd, tie by smaller sd and slight center bias to reduce oscillation.
            center_bias = -((nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2) * 1e-3
            val = (od - sd) * 1.0 - sd * 1e-4 + center_bias
            if val > local_best:
                local_best = val

        # Extra stability: prefer not moving if it's already very good
        if dx == 0 and dy == 0:
            local_best += 2e-3

        if local_best > best[0]:
            best = (local_best, dx, dy)

    return [best[1], best[2]]