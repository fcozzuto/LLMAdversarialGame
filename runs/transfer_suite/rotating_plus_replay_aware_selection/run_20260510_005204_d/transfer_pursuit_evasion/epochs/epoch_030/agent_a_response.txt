def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def dist(a, b, c, d):
        # Chebyshev fits diagonal movement and is capture-friendly
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best = None
    best_score = 10**9
    best_dxdy = (0, 0)

    # Greedy chase: minimize distance to opponent; slight preference for diagonal and toward target axes.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist(nx, ny, ox, oy)
        if d == 0:
            return [dx, dy]
        diag_bonus = 0 if (dx == 0 or dy == 0) else -0.01  # prefer diagonal when equally good
        axis_bonus = 0
        if dx != 0 and (ox - sx) * dx > 0:
            axis_bonus -= 0.005
        if dy != 0 and (oy - sy) * dy > 0:
            axis_bonus -= 0.005
        score = d + diag_bonus + axis_bonus
        if score < best_score:
            best_score = score
            best_dxdy = (dx, dy)

    if best_dxdy == (0, 0):
        # Fallback: pick any valid move that reduces manhattan distance.
        cur = abs(sx - ox) + abs(sy - oy)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                nd = abs(nx - ox) + abs(ny - oy)
                if nd < cur:
                    return [dx, dy]
        return [0, 0]

    return [best_dxdy[0], best_dxdy[1]]