def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    res_set = set(tuple(p) for p in resources)
    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Take any resource immediately (deterministic).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) in res_set and (nx, ny) not in obstacles:
            return [dx, dy]

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # For this move, choose the most "winnable" resource (largest margin).
        best_margin = -10**9
        best_selfd = 10**9
        for rx, ry in resources:
            selfd = dist8(nx, ny, rx, ry)
            oppd = dist8(ox, oy, rx, ry)
            margin = oppd - selfd  # positive means we are closer (likely to be first).
            if (margin > best_margin) or (margin == best_margin and selfd < best_selfd):
                best_margin = margin
                best_selfd = selfd

        # Prefer moves that improve our position vs opponent contested resources.
        stay_pen = 0 if (dx == 0 and dy == 0) else 1
        val = (best_margin, -best_selfd, stay_pen, -abs(nx - ox) - abs(ny - oy), -(dx * dx + dy * dy))
        if best is None or val > best[0]:
            best = (val, [dx, dy])

    return best[1] if best is not None else [0, 0]