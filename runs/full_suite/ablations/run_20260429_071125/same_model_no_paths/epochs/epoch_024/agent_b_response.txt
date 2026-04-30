def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not valid(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    opp_d_now = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if resources:
            d_res = min(cheb(nx, ny, rx, ry) for (rx, ry) in resources)
            nearest = None
            for (rx, ry) in resources:
                d = cheb(nx, ny, rx, ry)
                if nearest is None or d < nearest:
                    nearest = d
                    if d == d_res:
                        pass
        else:
            d_res = cheb(nx, ny, ox, oy)
            nearest = d_res

        d_opp = cheb(nx, ny, ox, oy)
        # Main objective: reduce distance to resources; tie-break: avoid opponent more when close.
        # Key is for minimization; convert to tuple with primary d_res, then -d_opp (via large offset).
        close_pen = 0 if opp_d_now > 2 else (2 - opp_d_now) * 10
        obstacle_pen = 0
        for ax, ay in blocked:
            if cheb(nx, ny, ax, ay) == 1:
                obstacle_pen = 2
                break

        primary = d_res + obstacle_pen + close_pen
        secondary = -d_opp
        tertiary = (dx == 0 and dy == 0)  # prefer moving
        key = (primary, secondary, tertiary, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]