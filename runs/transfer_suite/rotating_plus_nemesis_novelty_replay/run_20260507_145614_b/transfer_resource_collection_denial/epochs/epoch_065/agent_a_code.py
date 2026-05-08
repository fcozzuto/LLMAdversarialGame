def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        return [0 if sx == tx else (1 if tx > sx else -1),
                0 if sy == ty else (1 if ty > sy else -1)]

    for r in resources:
        if sx == r[0] and sy == r[1]:
            return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Target: most "swingy" resource (opponent farthest relative to us).
    best_r = None
    best_key = None
    for r in resources:
        rx, ry = r[0], r[1]
        myd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        key = (od - myd, -myd)  # maximize lead; break ties by closer to us
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    # If opponent is closer/equal, choose a move that maximizes our improvement on that same contested target.
    # Otherwise, simply step toward the best target.
    best = None
    best_val = None
    for dxi, dyi in moves:
        nx, ny = sx + dxi, sy + dyi
        if not inb(nx, ny):
            nx, ny = sx, sy
            dxi = dyi = 0
        myd = dist(nx, ny, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Add a small "anti-lag" term toward our nearest resource to avoid getting stuck.
        nearest = None
        for r in resources:
            rxx, ryy = r[0], r[1]
            d = dist(nx, ny, rxx, ryy)
            if nearest is None or d < nearest:
                nearest = d
        val = (od - myd, -myd, -nearest)
        if best_val is None or val > best_val:
            best_val = val
            best = (dxi, dyi)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]