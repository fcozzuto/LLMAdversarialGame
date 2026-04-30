def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        for rx, ry in resources:
            myd = dist((sx, sy), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            # Prefer resources where we're closer than opponent; break ties toward nearest overall.
            val = (opd - myd, -myd, -abs(rx - (w - 1 - ox)) - abs(ry - (h - 1 - oy)))
            if best is None or val > best[0]:
                best = (val, rx, ry)
        tx, ty = best[1], best[2]

    cx, cy = tx, ty
    desired = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = dist((nx, ny), (cx, cy))
            if desired is None or d < desired[0] or (d == desired[0] and (dx, dy) < desired[1]):
                desired = (d, (dx, dy))

    if desired is not None:
        return [int(desired[1][0]), int(desired[1][1])]

    return [0, 0]