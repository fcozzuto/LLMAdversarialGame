def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obst:
                resources.append((x, y))

    def dist_cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    best_move = None
    if resources:
        best = None
        best_score = None
        for rx, ry in resources:
            d = dist_cheb((sx, sy), (rx, ry))
            od = dist_cheb((ox, oy), (rx, ry))
            score = (d, -od)
            if best_score is None or score < best_score:
                best_score = score
                best = (rx, ry)
        if best is not None:
            tx, ty = best
            dx = 0
            if tx > sx: dx = 1
            elif tx < sx: dx = -1
            dy = 0
            if ty > sy: dy = 1
            elif ty < sy: dy = -1
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obst:
                return [dx, dy]

    cx, cy = w // 2, h // 2
    dx = 0
    if sx < cx: dx = 1
    elif sx > cx: dx = -1
    dy = 0
    if sy < cy: dy = 1
    elif sy > cy: dy = -1
    nx, ny = sx + dx, sy + dy
    if inside(nx, ny) and (nx, ny) not in obst:
        return [dx, dy]

    for ddx in (-1, 0, 1):
        for ddy in (-1, 0, 1):
            nx, ny = sx + ddx, sy + ddy
            if inside(nx, ny) and (nx, ny) not in obst:
                return [ddx, ddy]

    return [0, 0]