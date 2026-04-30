def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    def dist_cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    target = None
    if resources:
        best = None
        best_score = None
        for rx, ry in resources:
            d = dist_cheb((sx, sy), (rx, ry))
            od = dist_cheb((ox, oy), (rx, ry))
            score = (d, od)
            if best_score is None or score < best_score:
                best = (rx, ry)
                best_score = score
        target = best

    if target is not None:
        dx = target[0] - sx
        dy = target[1] - sy
        mx = 0 if dx == 0 else (1 if dx > 0 else -1)
        my = 0 if dy == 0 else (1 if dy > 0 else -1)
        cand = [(mx, my), (mx, 0), (0, my), (mx, -my) if my else (0, 0), (0, -my) if my else (0, 0)]
        for dxm, dym in cand:
            nx, ny = sx + dxm, sy + dym
            if (dxm, dym) == (0, 0):  # stay
                return [0, 0]
            if inside(nx, ny) and (nx, ny) not in obstacles:
                return [dxm, dym]
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    tx, ty = cx - sx, cy - sy
    dx = 0 if tx == 0 else (1 if tx > 0 else -1)
    dy = 0 if ty == 0 else (1 if ty > 0 else -1)
    if (sx + dx, sy + dy) not in obstacles and inside(sx + dx, sy + dy):
        return [dx, dy]
    # try a safe alternative move
    options = [(-1,-1), (-1,0), (0,-1), (1,-1), (1,0), (0,1), (-1,1), (1,1), (0,0)]
    for ddx, ddy in options:
        nx, ny = sx + ddx, sy + ddy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            return [ddx, ddy]
    return [0, 0]