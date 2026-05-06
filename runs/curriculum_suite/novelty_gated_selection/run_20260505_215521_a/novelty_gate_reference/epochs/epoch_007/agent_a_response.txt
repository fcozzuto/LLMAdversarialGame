def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    cx, cy = w // 2, h // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (-10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        if not resources:
            score = cheb(nx, ny, ox, oy) - 0.05 * cheb(nx, ny, cx, cy)
        else:
            score = -10**18
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                oppd = cheb(ox, oy, rx, ry)
                s = (oppd - myd) * 2.0 - 0.35 * myd
                if myd == 0:
                    s += 50.0
                if myd <= 1:
                    s += 1.0
                if s > score:
                    score = s
            score -= 0.02 * cheb(nx, ny, cx, cy)
        if score > best[0]:
            best = (score, dx if (nx, ny) != (sx, sy) else 0, dy if (nx, ny) != (sx, sy) else 0)
        elif score == best[0]:
            # deterministic tie-break: prefer staying closer to opponent, then center
            cur = cheb(nx, ny, ox, oy) + 0.01 * cheb(nx, ny, cx, cy)
            bestdx, bestdy = best[1], best[2]
            bx, by = sx + bestdx, sy + bestdy
            if not inb(bx, by) or (bx, by) in obstacles:
                bx, by = sx, sy
            bestv = cheb(bx, by, ox, oy) + 0.01 * cheb(bx, by, cx, cy)
            if cur < bestv:
                best = (score, dx if (nx, ny) != (sx, sy) else 0, dy if (nx, ny) != (sx, sy) else 0)

    return [best[1], best[2]]