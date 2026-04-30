def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # deterministic tie-break
    dirs.sort(key=lambda d: (d[0], d[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = (0, 0)
    bestv = -10**18

    if not res:
        # No visible resources: keep pressure by moving to increase distance to opponent while not wasting moves into edges.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obs:
                continue
            opp = cheb(nx, ny, ox, oy)
            # prefer safer center-ish position
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center = -(abs(nx - cx) + abs(ny - cy))
            v = (opp * 10) + center
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # With resources: choose move that maximizes (opponent distance - self distance) to some resource after the move.
    # Break ties by preferring closer resources and slightly farther from opponent.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        cur_best = -10**18
        for rx, ry in res:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # If we can become closer than opponent, advantage increases sharply; also prefer small self_d.
            adv = (opp_d - self_d)
            v = adv * 100 - self_d
            # small secondary: discourage going directly next to opponent if it doesn't help resources
            v -= cheb(nx, ny, ox, oy) * 0.5
            if v > cur_best:
                cur_best = v

        if cur_best > bestv:
            bestv, best = cur_best, (dx, dy)
    return [best[0], best[1]]