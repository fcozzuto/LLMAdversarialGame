def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    def pos_xy(v):
        if isinstance(v, dict):
            q = v.get("position", None)
        else:
            q = v
        if isinstance(q, (list, tuple)) and len(q) >= 2:
            return int(q[0]), int(q[1])
        return None

    blocked = set()
    for ob in observation.get("obstacles", []) or []:
        p = pos_xy(ob)
        if p is not None and 0 <= p[0] < w and 0 <= p[1] < h:
            blocked.add(p)

    resources = []
    for r in observation.get("resources", []) or []:
        p = pos_xy(r)
        if p is not None and 0 <= p[0] < w and 0 <= p[1] < h and p not in blocked:
            resources.append(p)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in blocked:
            continue
        if resources:
            dmin = 10**9
            for rp in resources:
                d = dist((nx, ny), rp)
                if d < dmin:
                    dmin = d
            sc = -dmin * 10 + dist((nx, ny), (ox, oy))
        else:
            sc = dist((nx, ny), (ox, oy)) * 10 - (abs(nx - w // 2) + abs(ny - h // 2))
        if sc > best_score:
            best_score = sc
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best