def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_xy(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        if isinstance(p, dict):
            if "position" in p:
                q = p["position"]
                if isinstance(q, (list, tuple)) and len(q) >= 2:
                    return int(q[0]), int(q[1])
            if "x" in p and "y" in p:
                return int(p["x"]), int(p["y"])
        return None

    obs = set()
    for t in observation.get("obstacles", []) or []:
        q = to_xy(t)
        if q is not None:
            obs.add(q)

    res = []
    for t in observation.get("resources", []) or []:
        q = to_xy(t)
        if q is not None:
            res.append(q)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        mind = 10**9
        for rx, ry in res:
            d = abs(nx - rx) + abs(ny - ry)
            if d < mind:
                mind = d
        d_op = abs(nx - ox) + abs(ny - oy)
        if res:
            score = -mind + 0.01 * d_op
        else:
            score = -d_op + 0.001 * (nx * w + ny)
        score = score + 1e-6 * (dx * 3 + dy)
        if best is None or score > best[0]:
            best = (score, dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]