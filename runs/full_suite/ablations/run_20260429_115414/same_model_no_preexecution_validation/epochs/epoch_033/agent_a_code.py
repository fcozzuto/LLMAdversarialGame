def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_dxdy = (0, 0)
    best_score = 10**18

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            candidates.append((nx, ny, dx, dy))
    if not candidates:
        return [0, 0]

    if res:
        for nx, ny, dx, dy in candidates:
            local_best = 10**18
            for rx, ry in res:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Prefer resources we can reach earlier; also reduce giving opponent advantage.
                val = ds - 0.65 * do
                if val < local_best:
                    local_best = val
            # Small preference for not moving if equally good; deterministic tie-break via tuple.
            score = local_best + 0.01 * (abs(dx) + abs(dy))
            if score < best_score:
                best_score = score
                best_dxdy = (dx, dy)
    else:
        # No visible resources: move toward center away from opponent lightly to stay flexible.
        tx = w // 2
        ty = h // 2
        for nx, ny, dx, dy in candidates:
            score = cheb(nx, ny, tx, ty) + 0.25 * cheb(nx, ny, ox, oy)
            if score < best_score:
                best_score = score
                best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]