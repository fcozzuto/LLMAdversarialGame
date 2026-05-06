def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Select best "contested" target deterministically
    best_t = None
    best_base = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer closer resources that opponent cannot reach quickly
        base = (60 - 6 * myd) + (20 - 4 * opd) + (1 if (rx in (0, w - 1) or ry in (0, h - 1)) else 0)
        # Slight bias toward resources nearer to center to avoid corner traps
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dcent = abs(rx - cx) + abs(ry - cy)
        base -= int(dcent)
        if base > best_base or (base == best_base and (rx, ry) < best_t):
            best_base = base
            best_t = (rx, ry)

    tx, ty = best_t

    # Choose move maximizing improvement for target while not allowing opponent to get closer to it
    best_m = (0, 0)
    best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy  # deterministic: treated as no-op if blocked by obstacle/outside
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Opponent diagonal_probe tends to pressure shortest route; we try to delay/compete
        s = (100 - 7 * myd2) - (40 - 4 * opd2)
        # Extra: move to reduce distance to target more than to "center the opponent"
        s += -2 * (abs(nx - ox) + abs(ny - oy))  # keep farther from opponent
        # Extra: if we can step onto a resource (not necessarily target), reward it
        if (nx, ny) in resources:
            s += 200
        if s > best_s or (s == best_s and (dx, dy) < best_m):
            best_s = s
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]