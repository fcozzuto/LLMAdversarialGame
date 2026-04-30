def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    # If resources exist, try to move toward the resource that maximizes
    # (opponent distance decrease) and (self distance decrease).
    if resources:
        best_r = None
        best_score = -10**9
        for r in resources:
            d_me = cheb((sx, sy), r)
            d_op = cheb((ox, oy), r)
            score = (d_op - d_me) * 12 - d_me
            if score > best_score:
                best_score = score
                best_r = r
        if best_r is not None:
            dx = 0
            dy = 0
            if best_r[0] > sx: dx = 1
            elif best_r[0] < sx: dx = -1
            if best_r[1] > sy: dy = 1
            elif best_r[1] < sy: dy = -1
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
            # else try to stay or step around obstacle
            for ddx in (-1, 0, 1):
                for ddy in (-1, 0, 1):
                    if ddx == 0 and ddy == 0:
                        continue
                    tx, ty = sx + ddx, sy + ddy
                    if valid(tx, ty):
                        return [ddx, ddy]

    # Fallback: move toward opponent if not blocked; otherwise try to sidestep
    dx = 0
    dy = 0
    if ox > sx: dx = 1
    elif ox < sx: dx = -1
    if oy > sy: dy = 1
    elif oy < sy: dy = -1
    nx, ny = sx + dx, sy + dy
    if valid(nx, ny):
        return [dx, dy]

    # Try immediate safe moves
    for ddx in (-1, 0, 1):
        for ddy in (-1, 0, 1):
            if ddx == 0 and ddy == 0:
                continue
            tx, ty = sx + ddx, sy + ddy
            if valid(tx, ty):
                return [ddx, ddy]

    # If all else fails, stay
    return [0, 0]