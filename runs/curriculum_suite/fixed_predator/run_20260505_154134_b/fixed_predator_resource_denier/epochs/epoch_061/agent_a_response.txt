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
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_val = None

    if not resources:
        tx, ty = w // 2, h // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = cheb(nx, ny, ox, oy) - cheb(nx, ny, tx, ty)
            cand = (v, cheb(nx, ny, tx, ty))
            if best_val is None or cand > best_val:
                best_val = cand
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # race: maximize advantage on best reachable resource
        best_adv = None
        best_sd = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if best_adv is None or (adv, -sd) > (best_adv, -best_sd):
                best_adv, best_sd = adv, sd
        if best_adv is None:
            continue
        # slight preference to reduce own distance in case of ties
        cand = (best_adv, -best_sd, -cheb(nx, ny, ox, oy), -(abs(nx - sx) + abs(ny - sy)))
        if best_val is None or cand > best_val:
            best_val = cand
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]