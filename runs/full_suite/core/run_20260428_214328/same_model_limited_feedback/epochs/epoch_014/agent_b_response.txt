def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def sqdist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if resources:
        best = None
        bx = by = 0
        for r in resources:
            d1 = sqdist((sx, sy), (r[0], r[1]))
            d2 = sqdist((ox, oy), (r[0], r[1]))
            val = d1 - 0.5 * d2
            if best is None or val < best:
                best = val
                bx, by = r[0], r[1]
        tx, ty = bx, by
    else:
        tx, ty = int(round(cx)), int(round(cy))

    moves = [-1, 0, 1]
    best_move = (0, 0)
    best_score = None
    for dx in moves:
        for dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            nd = sqdist((nx, ny), (tx, ty))
            no = sqdist((nx, ny), (ox, oy))
            score = nd - 0.1 * no
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
            elif score == best_score:
                if (dx, dy) < best_move:
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]