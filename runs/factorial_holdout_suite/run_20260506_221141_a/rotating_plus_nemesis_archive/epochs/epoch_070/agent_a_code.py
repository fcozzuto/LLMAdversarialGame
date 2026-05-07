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
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_value(cx, cy):
        best = -10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(cx, cy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            lead = od - sd  # positive means we likely arrive first
            # small deterministic obstacle/line penalty
            px = 0
            if rx != cx or ry != cy:
                ddx = 0
                if rx > cx: ddx = 1
                elif rx < cx: ddx = -1
                ddy = 0
                if ry > cy: ddy = 1
                elif ry < cy: ddy = -1
                nx, ny = cx + ddx, cy + ddy
                if (nx, ny) in obstacles:
                    px -= 2
                # also penalize being forced into obstacle-adjacent by direction
                mx1, my1 = rx, ry
                ax = nx - mx1
                if ax < 0: ax = -ax
                ay = ny - my1
                if ay < 0: ay = -ay
                if px == 0 and ax + ay > 0 and (nx, ny) in obstacles:
                    px -= 2
            # prefer closer resources only when tie in lead
            key = lead * 100 + (-sd) + px
            if key > best:
                best = key
        return best

    moves = [(0, 0), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        val = step_value(nx, ny)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]