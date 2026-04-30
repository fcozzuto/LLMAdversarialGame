def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    bestd = None
    best_r = None
    for r in resources:
        d = cheb((sx, sy), r)
        od = cheb((ox, oy), r)
        score = (od - d) * 10 - d
        if bestd is None or score > bestd or (score == bestd and (r < best_r)):
            bestd = score
            best_r = r
            best = r

    if best is not None:
        dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
        dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
        return [dx, dy]

    tx = 1 if (sx < ox) else -1
    ty = 1 if (sy < oy) else -1
    if sx == ox:
        tx = 0
    if sy == oy:
        ty = 0

    if (0 <= sx + tx < w) and (0 <= sy + ty < h) and ((sx + tx, sy + ty) not in obst):
        return [tx, ty]

    # If blocked, try simple fallback: move towards center or away from obstacle cluster deterministically
    cx, cy = w // 2, h // 2
    dx = 1 if cx > sx else -1 if cx < sx else 0
    dy = 1 if cy > sy else -1 if cy < sy else 0
    if (dx != 0 or dy != 0) and (0 <= sx + dx < w) and (0 <= sy + dy < h) and ((sx + dx, sy + dy) not in obst):
        return [dx, dy]

    # as last resort, stay
    return [0, 0]