def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    def to_xy(p):
        if isinstance(p, dict):
            v = p.get("position", None)
            if isinstance(v, (list, tuple)) and len(v) >= 2:
                return (v[0], v[1])
            if "x" in p and "y" in p:
                return (p["x"], p["y"])
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return (p[0], p[1])
        return None

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        q = to_xy(p)
        if q is not None:
            obst.add(q)

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        q = to_xy(p)
        if q is not None:
            res.append(q)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def best_target():
        if not res:
            return None
        best = None
        bd = 10**9
        for x, y in res:
            d = cheb(sx, sy, x, y)
            if d < bd or (d == bd and (x, y) < best):
                bd = d
                best = (x, y)
        return best

    target = best_target()

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        if target is None:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            d = cheb(nx, ny, cx, cy)
            val = -d
        else:
            tx, ty = target
            d_self = cheb(nx, ny, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            val = (d_opp - d_self)
            if d_self == 0:
                val += 10000
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]