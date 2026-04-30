def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    occ = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            occ.add((p[0], p[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_for_target(tx, ty):
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in occ:
                continue
            v = -cheb(nx, ny, tx, ty) * 10 + cheb(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return list(best)

    if resources:
        best_res = None
        best_d = 10**9
        for p in resources:
            if p is None or len(p) < 2:
                continue
            d = cheb(x, y, p[0], p[1])
            if d < best_d or (d == best_d and (best_res is None or (p[0], p[1]) < (best_res[0], best_res[1]))):
                best_d = d
                best_res = p
        if best_res is not None:
            return best_for_target(best_res[0], best_res[1])

    cx, cy = w // 2, h // 2
    return best_for_target(cx, cy)