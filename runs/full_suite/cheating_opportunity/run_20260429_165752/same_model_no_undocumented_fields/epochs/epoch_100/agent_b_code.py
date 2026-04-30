def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_mv = (0, 0)
    best_val = -10**18
    best_d = 10**18

    if not ok(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Contest resources: maximize (opp closer than us?) using distance advantage after the move.
    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            value = -10**18
            mind = 10**18
            for rx, ry in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                # Prefer resources where we are closer (opp_dist - our_dist), then break by our distance.
                v = d_op - d_me
                if v > value:
                    value, mind = v, d_me
                elif v == value and d_me < mind:
                    mind = d_me
            # Also lightly prefer moving away from obstacles' immediate danger by ensuring we can keep options.
            # (Deterministic: count viable neighbors.)
            neigh = 0
            for ddx, ddy in moves:
                if ddx == 0 and ddy == 0:
                    continue
                tx, ty = nx + ddx, ny + ddy
                if ok(tx, ty):
                    neigh += 1
            value = value * 2 + neigh
            if value > best_val or (value == best_val and mind < best_d):
                best_val, best_d, best_mv = value, mind, (dx, dy)
    else:
        # No resources: push toward center to reduce distance to future resources (or symmetry).
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                d = cheb(nx, ny, cx, cy)
                if d < best_d:
                    best_d = d
                    best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]