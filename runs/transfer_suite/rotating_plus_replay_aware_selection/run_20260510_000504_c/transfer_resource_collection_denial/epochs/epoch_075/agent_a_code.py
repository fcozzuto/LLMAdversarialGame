def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, dict):
            q = p.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obstacles.add((int(q[0]), int(q[1])))
            elif "x" in p and "y" in p:
                obstacles.add((int(p["x"]), int(p["y"])))
        elif isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                resources.append((int(q[0]), int(q[1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    target = None
    if resources:
        bestd = None
        for x, y in resources:
            d = abs(sx - x) + abs(sy - y)
            if blocked(x, y):
                continue
            if bestd is None or d < bestd or (d == bestd and (x, y) < target):
                bestd = d
                target = (x, y)
    if target is None:
        target = (ox, oy)

    tx, ty = target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = [(dx, dy), (dx, 0), (0, dy), (-dx, dy), (dx, -dy), (-dx, 0), (0, -dy), (0, 0)]
    for cdx, cdy in candidates:
        nx, ny = sx + cdx, sy + cdy
        if in_bounds(nx, ny) and not blocked(nx, ny):
            return [int(cdx), int(cdy)]
    for cdx in (-1, 0, 1):
        for cdy in (-1, 0, 1):
            nx, ny = sx + cdx, sy + cdy
            if in_bounds(nx, ny) and not blocked(nx, ny):
                return [int(cdx), int(cdy)]
    return [0, 0]