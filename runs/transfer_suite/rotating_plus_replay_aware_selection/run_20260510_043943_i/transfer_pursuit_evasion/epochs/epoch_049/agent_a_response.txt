def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role_self = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role_self) or ("pursuer" not in role_self and "hunter" not in role_self and "chaser" not in role_self)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def corner_score(x, y):
        best = 0
        for cx, cy in corners:
            d = cheb(x, y, cx, cy)
            if d > best:
                best = d
        return best

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_opp = cheb(nx, ny, ox, oy)
        # local obstacle deterrent: prefer moves with more free neighbors
        free_n = 0
        for ddx, ddy in dirs:
            tx, ty = nx + ddx, ny + ddy
            if valid(tx, ty):
                free_n += 1
        if is_evader:
            val = (-d_to_opp) - 0.05 * (corner_score(nx, ny)) - 0.01 * free_n
        else:
            # pursuer: drive distance down, slightly prefer tighter turns near opponent and open space
            val = (d_to_opp) - 0.005 * free_n
            # if on same row/col/diag, prioritize that direction by reducing max(|dx|,|dy|)
        better = (best_val is None) or (val < best_val)
        if better:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]