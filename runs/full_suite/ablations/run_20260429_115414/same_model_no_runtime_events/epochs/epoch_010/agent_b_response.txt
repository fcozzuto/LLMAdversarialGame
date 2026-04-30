def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    oppd0 = cheb(sx, sy, ox, oy)

    best = (0, 0); bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        v = 0
        v += -3 * cheb(nx, ny, ox, oy)

        if resources:
            # Target resources where we can arrive sooner than opponent, and avoid those opponent can take.
            for r in resources:
                if not r or len(r) < 2:
                    continue
                rx, ry = r[0], r[1]
                if (rx, ry) in obs:
                    continue
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                drel = od - sd
                if drel > 0:
                    v += 60 * drel + 25 // (1 + sd)
                else:
                    v -= 55 * (-drel) + 20 // (1 + od)
        else:
            # No visible resources: drift toward center while keeping distance from opponent.
            cx, cy = (3, 3) if (sx + sy) <= 7 else (4, 4)
            v += -cheb(nx, ny, cx, cy) + (2 if cheb(nx, ny, ox, oy) > oppd0 else 0)

        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]