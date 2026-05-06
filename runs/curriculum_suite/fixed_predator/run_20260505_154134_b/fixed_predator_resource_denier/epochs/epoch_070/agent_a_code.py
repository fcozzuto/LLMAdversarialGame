def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = -cheb(nx, ny, tx, ty)
            if best is None or (v, -abs(dx) - abs(dy)) > best:
                best = (v, dx, dy)
        return [best[1], best[2]] if best is not None else [0, 0]

    def min_dist_to_resources(px, py):
        md = None
        for rx, ry in resources:
            d = cheb(px, py, rx, ry)
            if md is None or d < md:
                md = d
        return md if md is not None else 999

    cur_self_min = min_dist_to_resources(sx, sy)
    best_key = None
    best_move = (0, 0)

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        self_min = min_dist_to_resources(nx, ny)
        opp_min = min_dist_to_resources(ox, oy)

        progress = cur_self_min - self_min  # positive if closer
        hit = 1 if (nx, ny) in set((r[0], r[1]) for r in resources) else 0
        dist_adv = opp_min - self_min

        key = (hit * 1000 + dist_adv * 20 + progress * 5, -cheb(nx, ny, ox, oy), -abs(dx) - abs(dy), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]