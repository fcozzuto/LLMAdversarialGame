def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def passable(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def manh(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    cx, cy = w // 2, h // 2
    if not resources:
        target = (cx, cy)
    else:
        best = None
        bestv = 10**18
        for rx, ry in resources:
            v = cheb(sx, sy, rx, ry)
            # Prefer resources that are closer than opponent (deterministically)
            vo = cheb(ox, oy, rx, ry)
            v += 0 if vo > v else 2
            if v < bestv:
                bestv = v
                best = (rx, ry)
        target = best if best is not None else (cx, cy)

    best_move = (0, 0)
    best_score = -10**18
    tx, ty = target

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            continue

        dist_to_t = cheb(nx, ny, tx, ty)

        # Obstacle repulsion (deterministic, local)
        rep = 0
        for (px, py) in obstacles:
            md = manh(nx, ny, px, py)
            if md <= 2:
                rep += (3 - md) * 5

        # Avoid moving into tight corridors: penalize having obstacles adjacent
        adj_obs = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                ax, ay = nx + ex, ny + ey
                if (ax, ay) in obstacles:
                    adj_obs += 1

        # Slightly prefer increasing distance from opponent to reduce contention
        dist_from_o = cheb(nx, ny, ox, oy)

        score = -dist_to_t * 10 + dist_from_o * 1.5 + rep * 2 - adj_obs * 3
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]