def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def neigh_obst_pen(x, y):
        if not inb(x, y):
            return 10**9
        if (x, y) in obstacles:
            return 10**8
        p = 0
        for dx, dy in [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1),(0,0)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                p += 3
        return p

    def best_target(cx, cy):
        if not resources:
            return ( (w - 1) // 2, (h - 1) // 2 )
        best = resources[0]
        bestd = cheb(cx, cy, best[0], best[1])
        for rx, ry in resources[1:]:
            d = cheb(cx, cy, rx, ry)
            if d < bestd:
                bestd = d
                best = (rx, ry)
        return best

    tx, ty = best_target(sx, sy)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        pen = neigh_obst_pen(nx, ny)
        if pen >= 10**8:
            continue

        dist = cheb(nx, ny, tx, ty)
        opp_dist = cheb(nx, ny, ox, oy)

        # Prefer moving closer to target; stay safer and slightly away from opponent.
        val = (-dist * 5) + (opp_dist * 0.8) - pen * 1.2

        # If we can reach a resource this step, bias strongly.
        if resources:
            for rx, ry in resources:
                if cheb(nx, ny, rx, ry) == 0:
                    val += 50

        # Deterministic tie-breaker: smallest lexicographic (dx,dy)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]