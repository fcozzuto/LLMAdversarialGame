def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if resources:
        best = None  # (priority, -gain, dist_to_resource, dx, dy)
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            gain = 1 if ds <= do else 0
            # Prefer resources we can reach no later than opponent; otherwise pick closest anyway.
            priority = 0 if ds <= do else 1
            for dx, dy, nx, ny in legal:
                dn = dist(nx, ny, rx, ry)
                val = (priority, -gain, dn)
                if best is None or val < best[0]:
                    best = (val, dx, dy)
        return [best[1], best[2]]

    # No visible resources: move toward center (deterministic escape).
    tx, ty = (w - 1) // 2, (h - 1) // 2
    best = None
    for dx, dy, nx, ny in legal:
        d = dist(nx, ny, tx, ty)
        if best is None or d < best[0]:
            best = (d, dx, dy)
    return [best[1], best[2]]