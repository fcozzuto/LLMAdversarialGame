def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in (observation.get("obstacles") or []):
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    if resources:
        best_r = None
        best_d = None
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if best_d is None or d < best_d or (d == best_d and (rx, ry) < best_r):
                best_d = d
                best_r = (rx, ry)
        tx, ty = best_r
        d_self = best_d
        d_opp = min(cheb(ox, oy, tx, ty), 10**9)
        chase = not (d_opp < d_self)
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        chase = True

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        if chase:
            val = -cheb(nx, ny, tx, ty)
            # small tie-break: prefer moving away from opponent when close
            val -= 0.01 * cheb(nx, ny, ox, oy)
        else:
            # when opponent threatens, prioritize distance from opponent
            val = cheb(nx, ny, ox, oy)
            # and still nudge toward target lightly
            val += -0.001 * cheb(nx, ny, tx, ty)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]