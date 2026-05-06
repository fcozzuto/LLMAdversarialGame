def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

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

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        bests = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            sc = -cheb(nx, ny, tx, ty)
            if best is None or sc > bests:
                best, bests = (dx, dy), sc
        return [best[0], best[1]]

    def pos_from_res(r):
        if isinstance(r, dict):
            return (r.get("x", r.get("pos", (None, None))[0]), r.get("y", r.get("pos", (None, None))[1]))
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return (r[0], r[1])
        return (None, None)

    res_pos = []
    for r in resources:
        rx, ry = pos_from_res(r)
        if rx is not None and ry is not None:
            res_pos.append((rx, ry))
    if not res_pos:
        return [0, 0]

    my_t = min(res_pos, key=lambda p: cheb(sx, sy, p[0], p[1]))
    opp_t = min(res_pos, key=lambda p: cheb(ox, oy, p[0], p[1]))

    best = None
    bests = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        d_my = cheb(nx, ny, my_t[0], my_t[1])
        d_opp = cheb(nx, ny, opp_t[0], opp_t[1])
        d_self_opp = cheb(nx, ny, ox, oy)
        sc = -2 * d_my - 1 * d_opp - 0.2 * d_self_opp
        if (nx, ny) == my_t:
            sc += 5
        if (nx, ny) == opp_t:
            sc += 2
        if best is None or sc > bests:
            best, bests = (dx, dy), sc

    return [best[0], best[1]]