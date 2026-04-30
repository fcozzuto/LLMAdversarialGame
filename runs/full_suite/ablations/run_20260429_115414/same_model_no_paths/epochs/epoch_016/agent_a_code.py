def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b, c, d):
        da = a - c
        if da < 0: da = -da
        db = b - d
        if db < 0: db = -db
        return da + db

    def good_move(nx, ny):
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            return None
        if resources:
            best = None
            for rx, ry in resources:
                ds = dist(nx, ny, rx, ry)
                do = dist(nx, ny, ox, oy)
                # Prefer getting closer to resources than opponent; tie-break by resource order
                val = (ds - dist(ox, oy, rx, ry), ds, do)
                if best is None or val < best[0]:
                    best = (val, rx, ry)
            return (best[0][0], best[0][1], best[0][2], nx, ny)
        # No visible resources: keep distance from opponent
        return (0, -dist(nx, ny, ox, oy), 0, nx, ny)

    best_ret = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        key = good_move(nx, ny)
        if key is None:
            continue
        if best_key is None or key < best_key:
            best_key = key
            best_ret = [dx, dy]

    if best_ret is None:
        return [0, 0]
    return best_ret