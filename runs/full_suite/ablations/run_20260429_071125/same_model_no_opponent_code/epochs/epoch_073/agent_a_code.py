def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if any(r[0] == sx and r[1] == sy for r in resources):
        return [0, 0]

    def nearest_dist(x, y):
        if not resources:
            return 10**9
        best = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best:
                best = d
        return best

    best = None
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sd = nearest_dist(nx, ny)
        od = nearest_dist(ox + (nx - sx), oy + (ny - sy))
        val = (od - sd) * 10 - sd
        # also slightly prefer staying within bounds and not moving into opponent immediate vicinity
        val -= cheb(nx, ny, ox, oy)
        key = (val, -abs(dx) - abs(dy), -dx, -dy)
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    dx, dy = best_move if best is not None else (0, 0)
    return [int(dx), int(dy)]