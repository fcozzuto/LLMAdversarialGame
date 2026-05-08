def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = (0, 0)
    best_key = None
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx * ddx + ddy * ddy
        manh = abs(ddx) + abs(ddy)
        # Prefer staying in-bounds away from edges; also avoid moving onto opponent.
        edge_pen = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
        center_score = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        # Key: maximize dist2, then maximize manh, then maximize center_score, then minimize edge_pen.
        key = (dist2, manh, center_score, -edge_pen)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]