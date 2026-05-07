def choose_move(observation):
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = set()
    for it in (observation.get("obstacles") or []):
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh:
                obstacles.add((x, y))
    resources = []
    for it in (observation.get("resources") or []):
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        tx, ty = gw // 2, gh // 2
    else:
        def dist(x1, y1, x2, y2):
            dx = x1 - x2
            if dx < 0: dx = -dx
            dy = y1 - y2
            if dy < 0: dy = -dy
            return dx if dx > dy else dy
        best_intercept = None
        best_intercept_val = None
        best_collect = None
        best_collect_val = None
        for (rx, ry) in resources:
            sd = dist(sx, sy, rx, ry)
            od = dist(ox, oy, rx, ry)
            delta = od - sd  # positive: we are closer
            if best_collect is None or (delta, -sd, -rx, -ry) > best_collect_val:
                best_collect = (rx, ry)
                best_collect_val = (delta, -sd, -rx, -ry)
            # If opponent is closer, try to deny by moving toward that contested resource.
            if od < sd:
                val = (sd - od, -sd, rx, ry)  # prioritize smallest contest gap? use sd-od large
                if best_intercept is None or val > best_intercept_val:
                    best_intercept = (rx, ry)
                    best_intercept_val = val
        tx, ty = best_intercept if best_intercept is not None else best_collect
    def safe(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b
    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        # also consider not giving opponent a huge lead into our target
        d_opp = cheb(ox, oy, tx, ty)
        val = (-d_self, sd := -d_self, -(d_opp - d_self), -abs(nx - ox) - abs(ny - oy))
        # deterministic tie-break with position ordering
        val = (val, nx, ny)
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]