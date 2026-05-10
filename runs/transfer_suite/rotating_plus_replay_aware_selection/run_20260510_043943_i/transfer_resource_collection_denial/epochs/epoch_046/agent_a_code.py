def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

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

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def adj_obst(x, y):
        c = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                c += 1
        return c

    def cell_score_from(px, py):
        if not resources:
            tx, ty = (w - 1) // 2, (h - 1) // 2
            return -cheb(px, py, tx, ty) - 0.01 * adj_obst(px, py)
        best = -10**18
        for rx, ry in resources:
            sd = cheb(px, py, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            # prefer grabbing before opponent, but also prefer being closer overall
            v = adv * 100 - sd * 2
            if sd == 0:
                v += 10**6
            elif sd == 1:
                v += 2 * 10**4
            # mild deterministic preference among ties
            v += -(rx * 7 + ry * 11) * 1e-3
            best = v if v > best else best
        # small penalty for moving near obstacles
        return best - 0.2 * adj_obst(px, py)

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            nx, ny = sx, sy
        v = cell_score_from(nx, ny)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    return best_move