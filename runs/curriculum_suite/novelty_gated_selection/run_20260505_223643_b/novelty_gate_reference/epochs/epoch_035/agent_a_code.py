def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0] or 0), int(sp[1] or 0)
    ox, oy = int(op[0] or 0), int(op[1] or 0)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(a, b, c, d):
        ddx = a - c
        if ddx < 0: ddx = -ddx
        ddy = b - d
        if ddy < 0: ddy = -ddy
        return ddx + ddy

    res_list = []
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if inside(rx, ry):
            res_list.append((rx, ry))
    if not res_list:
        res_list = [(ox, oy)]  # fallback

    best = None
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            oppd = dist(nx, ny, ox, oy)
            mind = 10**9
            for rx, ry in res_list:
                d = dist(nx, ny, rx, ry)
                if d < mind:
                    mind = d
            score = -mind + 0.6 * oppd
            if score > best_score:
                best_score = score
                best = (dx, dy)

    if best is None:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                    return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]