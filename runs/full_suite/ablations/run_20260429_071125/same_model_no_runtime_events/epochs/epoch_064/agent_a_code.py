def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def step_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
            if dx != 0:
                nx = sx + dx
                ny = sy
                if 0 <= nx < w and (nx, ny) not in obstacles:
                    return [dx, 0]
            if dy != 0:
                nx = sx
                ny = sy + dy
                if 0 <= ny < h and (nx, ny) not in obstacles:
                    return [0, dy]
            for ddx in (-1, 0, 1):
                for ddy in (-1, 0, 1):
                    if ddx == 0 and ddy == 0:
                        continue
                    nx, ny = sx + ddx, sy + ddy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                        return [ddx, ddy]
            return [0, 0]
        return [dx, dy]

    # Evaluate resources by: prefer where we are not worse than opponent; then prefer shorter distance; then lexicographic.
    best = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # primary: we want opd - myd large (we closer); secondary: myd small; tertiary: lexicographic
        key = (-(opd - myd), myd, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    _, (tx, ty) = best

    if sx == tx and sy == ty:
        return [0, 0]
    return step_toward(tx, ty)