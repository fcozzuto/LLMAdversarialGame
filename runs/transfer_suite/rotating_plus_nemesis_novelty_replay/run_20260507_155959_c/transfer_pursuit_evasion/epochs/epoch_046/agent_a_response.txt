def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        d_opp = abs(ox - nx) + abs(oy - ny)

        # "Cut-off" heuristic: prefer moves that reduce opponent's ability to stay far from us
        # by also minimizing their distance to the farthest corner after we advance.
        far_c = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        corner_pressure = abs(far_c[0] - nx) + abs(far_c[1] - ny)

        # If opponent is near a corner, prioritize aligning to their adjacent squares (more direct capture).
        near_corner = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        adj_x = near_corner[0] + (1 if ox == near_corner[0] and ox == 0 else (-1 if ox == near_corner[0] else 0) if ox != near_corner[0] else 0)
        adj_y = near_corner[1] + (1 if oy == near_corner[1] and oy == 0 else (-1 if oy == near_corner[1] else 0) if oy != near_corner[1] else 0)
        # keep it safe; if computed adj is out, ignore
        align = 0
        if valid(ox, oy):
            align = -man((nx, ny), (ox + (1 if ox < (w - 1) else (-1 if ox > 0 else 0)), oy + (1 if oy < (h - 1) else (-1 if oy > 0 else 0))))

        # Value: primarily minimize distance to opponent; secondarily reduce corner escape.
        val = -100 * d_opp - 0.8 * corner_pressure + 0.2 * align

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]