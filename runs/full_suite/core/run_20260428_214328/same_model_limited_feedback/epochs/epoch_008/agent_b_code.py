def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    grid_w = observation.get("grid_width", 8)
    grid_h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obs_raw = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obs_raw)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < grid_w and 0 <= ny < grid_h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    if resources:
        best = None
        for dx, dy, nx, ny in candidates:
            best_val = None
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                sd = dist2(nx, ny, rx, ry)
                od = dist2(ox, oy, rx, ry)
                val = (od - sd) * 100000 - sd - dist2(nx, ny, ox, oy)
                if best_val is None or val > best_val:
                    best_val = val
            if best_val is None:
                best_val = -dist2(nx, ny, ox, oy)
            tup = (-best_val, dx, dy)
            if best is None or tup < best:
                best = tup
        return [best[1], best[2]]

    best = None
    for dx, dy, nx, ny in candidates:
        val = dist2(nx, ny, ox, oy)
        tup = (-val, dx, dy)
        if best is None or tup < best:
            best = tup
    return [best[1], best[2]]