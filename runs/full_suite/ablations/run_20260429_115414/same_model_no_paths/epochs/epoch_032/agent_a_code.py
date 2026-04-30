def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is None or len(b) < 2:
            continue
        bx, by = int(b[0]), int(b[1])
        if 0 <= bx < w and 0 <= by < h:
            obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r is None or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = sorted(dirs, key=lambda d: (d[0] == 0 and d[1] == 0, d[0], d[1]))  # deterministic preference order

    def best_resource_dist(x, y):
        if not resources:
            return cheb(x, y, ox, oy)
        best = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best:
                best = d
        return best

    def best_score_for(x, y):
        if (x, y) in obstacles or not (0 <= x < w and 0 <= y < h):
            return None
        md = best_resource_dist(x, y)
        od = cheb(x, y, ox, oy)
        # minimize distance to resources, but avoid getting too close to opponent
        # (scale kept small and deterministic)
        val = md - (od * 0.25)
        # tiny tie-breakers to reduce dithering: prefer advancing towards center and away from staying put
        center_bias = abs(x - (w - 1) / 2.0) + abs(y - (h - 1) / 2.0)
        val += center_bias * 0.01
        return val

    best_move = (0, 0)
    best_val = 10**18
    # If resources exist, also bias toward the globally nearest resource direction deterministically.
    anchor = None
    if resources:
        bestd = 10**9
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                anchor = (rx, ry)
        ax, ay = anchor
    else:
        ax, ay = ox, oy

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = best_score_for(nx, ny)
        if v is None:
            continue
        if dx == 0 and dy == 0 and resources:
            v += 0.02  # discourage idle when resources exist
        if resources:
            # directional tie-break: prefer reducing cheb distance to the current nearest-resource anchor
            v += (cheb(nx, ny, ax, ay) - cheb(sx, sy, ax, ay)) * 0.001
        if v < best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]