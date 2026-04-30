def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    best = None
    best_tuple = (-10**9, 10**9, 0)

    if resources:
        for i, (dx, dy) in enumerate(moves):
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            myd = cheb(nx, ny, ox, oy)
            gain = -10**9
            best_res_dist = 10**9
            for rx, ry in resources:
                md = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                g = od - md
                if g > gain or (g == gain and md < best_res_dist):
                    gain = g
                    best_res_dist = md
            t = (gain, -best_res_dist, -i)
            if best is None or t > best_tuple:
                best_tuple = t
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    # No resources or all blocked: maximize distance from opponent (safe, deterministic)
    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        t = (d, -i)
        if best is None or t > best_tuple:
            best_tuple = t
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]