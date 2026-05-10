def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    role = str(observation.get("self_role", "")).lower()
    evader = ("evader" in role) or ("runner" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def bad(x, y):
        return (x, y) in blocked

    def score_at(x, y):
        if bad(x, y) or not inb(x, y):
            return -10**9
        rdist = min((cheb(x, y, rx, ry) for rx, ry in res), default=10**6)
        odist = cheb(x, y, ox, oy)
        corner_bias = min(cheb(ox, oy, cx, cy) for cx, cy in corners)
        avoid = (1 if evader else -1)  # evader prefers farther from opponent
        return (-rdist * 3) + (odist * avoid * 2) + (0 if not res else 0) + (1 if corner_bias > 0 else 0)

    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        x, y = sx + dx, sy + dy
        v = score_at(x, y)
        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best