def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def get_xy(p):
        if isinstance(p, dict):
            if "position" in p:
                q = p["position"]
                return (q[0], q[1]) if isinstance(q, (list, tuple)) and len(q) >= 2 else None
            if "x" in p and "y" in p:
                return (p["x"], p["y"])
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return (p[0], p[1])
        return None

    obst = set()
    for p in obstacles:
        q = get_xy(p)
        if q is not None:
            obst.add(q)

    res = []
    for p in resources:
        q = get_xy(p)
        if q is not None:
            res.append(q)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if res:
        target = min(res, key=lambda t: cheb(sx, sy, t[0], t[1]))
        cx, cy = target
    else:
        cx, cy = w // 2, h // 2

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        myd = cheb(nx, ny, cx, cy)
        oppd = cheb(nx, ny, ox, oy)
        val = (-(myd), oppd, 0 if (nx, ny) == (sx, sy) else 1, dx, dy)
        if best is None or val > best[0]:
            best = (val, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]