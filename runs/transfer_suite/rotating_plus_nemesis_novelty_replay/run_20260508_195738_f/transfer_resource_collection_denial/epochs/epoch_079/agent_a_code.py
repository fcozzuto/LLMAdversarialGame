def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    obs = observation.get("obstacles", []) or []
    for p in obs:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    resources = []
    rs = observation.get("resources", []) or []
    for r in rs:
        try:
            resources.append((int(r[0]), int(r[1])))
        except Exception:
            pass

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = (0, 0) if ((ox + oy) % 2 == 0) else (w - 1, h - 1)
    else:
        best = None
        for rx, ry in resources:
            d_self = cheb(sx, sy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # prefer resources we can reach not later than opponent; tie-break by closer to us
            key = (0 if d_self <= d_opp else 1, d_self, d_opp, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]

    best_move = (10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # slight bias to stay when already at target
        if nx == tx and ny == ty:
            d -= 0.1
        # small deterministic penalty to reduce oscillations
        d += 0.01 * (abs(dx) + abs(dy))
        if d < best_move[0]:
            best_move = (d, dx, dy)

    return [int(best_move[1]), int(best_move[2])]