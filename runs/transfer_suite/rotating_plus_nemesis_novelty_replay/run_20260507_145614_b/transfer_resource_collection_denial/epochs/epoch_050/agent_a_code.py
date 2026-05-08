def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    best_r = None
    best_val = -10**9
    for rx, ry in resources:
        if (rx, ry) == (sx, sy):
            return [0, 0]
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # prefer resources where we are closer; if we're behind, prefer the ones we can steal soon
        val = (od - sd) * 3 - sd
        if sd == 0:
            val += 1000
        if val > best_val:
            best_val = val
            best_r = (rx, ry)

    rx, ry = best_r
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_s = -10**18
    for dxi, dyi in moves:
        nx, ny = sx + dxi, sy + dyi
        if not inb(nx, ny):
            continue
        ns = cheb(nx, ny, rx, ry)
        os = cheb(ox, oy, rx, ry)
        # primary: get closer to target; secondary: if we are behind, reduce opponent advantage; tertiary: avoid edging too far away from center late not needed
        s = -ns
        if ns <= os:
            s += 10 + (os - ns) * 2
        else:
            s -= (ns - os) * 3
        # slight preference to not immediately worsen self distance to any resource nearby (steal potential)
        # (deterministic, limited work)
        if resources:
            for j in range(0, len(resources), 3):
                rx2, ry2 = resources[j]
                if (rx2, ry2) == (nx, ny):
                    s += 200
                else:
                    s += max(0, 2 - (cheb(nx, ny, rx2, ry2) - cheb(sx, sy, rx2, ry2)))
        if s > best_s:
            best_s = s
            best_m = (dxi, dyi)
    return [best_m[0], best_m[1]]