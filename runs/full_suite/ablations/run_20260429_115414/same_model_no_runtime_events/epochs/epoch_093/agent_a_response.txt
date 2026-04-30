def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        target = (tx, ty)
    else:
        best = resources[0]
        best_adv = -10**9
        mx, my = (sx + ox) // 2, (sy + oy) // 2
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = (od - sd) * 10 - cheb(rx, ry, mx, my)
            if adv > best_adv:
                best_adv = adv
                best = (rx, ry)
        target = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    tx, ty = target
    opponent_pressure = (len(resources) if resources else 0) + 1

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        base = 1000 - sd * 25
        intercept = (od - sd) * 40
        near_self = -cheb(nx, ny, ox, oy) * 3  # small penalty for being too close to opponent (avoid collisions)
        if resources:
            # extra reward if we reduce opponent advantage on the closest remaining resource
            closest = None
            closest_val = 10**9
            for rx, ry in resources:
                v = cheb(nx, ny, rx, ry)
                if v < closest_val:
                    closest_val = v
                    closest = (rx, ry)
            cx, cy = closest
            oppc = cheb(ox, oy, cx, cy)
            steal = (oppc - closest_val) * (20 + opponent_pressure)
        else:
            steal = 0
        score = base + intercept + near_self + steal
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]