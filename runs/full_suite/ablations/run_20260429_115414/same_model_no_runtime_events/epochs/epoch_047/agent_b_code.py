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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    rem = observation.get("remaining_resource_count")
    try:
        rem = int(rem or 0)
    except:
        rem = 0
    late = rem <= 3

    if resources:
        best_r = None
        best_metric = None
        for (rx, ry) in resources:
            d_s = cheb(sx, sy, rx, ry)
            d_o = cheb(ox, oy, rx, ry)
            metric = (d_o - d_s) * 1000 + (-d_s)
            if best_metric is None or metric > best_metric:
                best_metric = metric
                best_r = (rx, ry)
        tx, ty = best_r
        best_move = (0, 0)
        best_val = None
        opp_now = cheb(sx, sy, ox, oy)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                nx, ny = sx, sy
                dx, dy = 0, 0
            d_new = cheb(nx, ny, tx, ty)
            d_opp = cheb(nx, ny, ox, oy)
            # Prefer taking contested resources, and avoid getting too close to opponent.
            val = (-d_new) * 100 + d_opp - (opp_now - d_new) * (3 if late else 1)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: drift away from opponent.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        d_opp = cheb(nx, ny, ox, oy)
        val = d_opp
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]