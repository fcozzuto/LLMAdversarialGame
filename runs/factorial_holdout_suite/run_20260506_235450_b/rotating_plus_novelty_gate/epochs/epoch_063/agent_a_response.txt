def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def blocked(x, y):
        return (x, y) in obs or not (0 <= x < w and 0 <= y < h)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def score_resource(rx, ry):
        if blocked(rx, ry):
            return None
        du = cheb(sx, sy, rx, ry)
        dov = cheb(ox, oy, rx, ry)
        # Relative advantage first; if similar, take the one we can reach sooner.
        return (dov - du) * 100 - du

    if not resources:
        return [0, 0]

    best = None
    best_s = -10**18
    best_du = 10**9
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if isinstance(rx, int) and isinstance(ry, int):
                s = score_resource(rx, ry)
                if s is None:
                    continue
                du = cheb(sx, sy, rx, ry)
                if s > best_s or (s == best_s and du < best_du):
                    best_s = s
                    best_du = du
                    best = (rx, ry)

    rx, ry = best if best is not None else (sx, sy)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_d = 10**9
    best_rel = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d = cheb(nx, ny, rx, ry)
        dov_next = cheb(ox, oy, rx, ry)
        # If we can't significantly improve time, avoid moving away from resources the opponent is close to.
        rel = dov_next - d
        if d < best_d or (d == best_d and rel > best_rel):
            best_d = d
            best_rel = rel
            best_m = (dx, dy)

    if best_m == (0, 0) and blocked(sx, sy):
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]