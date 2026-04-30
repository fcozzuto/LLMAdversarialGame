def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = (int(x) for x in observation.get("self_position", [0, 0]))
    ox, oy = (int(x) for x in observation.get("opponent_position", [w - 1, h - 1]))
    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))
    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy
    best = None
    bestd = None
    for r in resources:
        d = cheb((sx, sy), r)
        if bestd is None or d < bestd or (d == bestd and r < best):
            best = r
            bestd = d
    if best is not None:
        dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
        dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
        return [dx, dy]
    # no resources: move to balance between corners
    tx, ty = (w - 1, 0) if (sx + sy) <= (ox + oy) else (0, h - 1)
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    return [dx, dy]