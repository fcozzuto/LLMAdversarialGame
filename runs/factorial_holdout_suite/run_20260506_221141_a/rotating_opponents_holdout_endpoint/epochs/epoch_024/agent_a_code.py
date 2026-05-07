def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_in = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_key = None
    for rx, ry in res:
        md = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Prefer resources where we are closer (denier-aware); small deterministic bias
        key = (md - 0.9 * od, md, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    best_move = None
    best_val = None
    for dx, dy, nx, ny in legal:
        md2 = dist(nx, ny, rx, ry)
        od2 = dist(ox, oy, rx, ry)
        # If we're already on a resource, keep still deterministically
        if nx == rx and ny == ry:
            val = (-1e9, 0, dx, dy)
        else:
            val = (md2 - 0.9 * od2, md2, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]