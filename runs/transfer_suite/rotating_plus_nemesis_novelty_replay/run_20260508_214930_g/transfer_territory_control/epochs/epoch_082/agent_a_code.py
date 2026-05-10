def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    resources = observation.get("resources") or []
    unclaimed = observation.get("unclaimed_cells") or []
    remaining = observation.get("remaining_resource_count", None)

    tx = ty = None
    if (remaining is None or remaining > 0) and resources:
        best = None
        for p in resources:
            x, y = p
            if ok(x, y):
                d = dist(sx, sy, x, y)
                if best is None or d < best[0]:
                    best = (d, x, y)
        if best is not None:
            tx, ty = best[1], best[2]
    if tx is None and unclaimed:
        best = None
        for p in unclaimed:
            x, y = p
            if ok(x, y):
                d = dist(sx, sy, x, y)
                if best is None or d < best[0]:
                    best = (d, x, y)
        if best is not None:
            tx, ty = best[1], best[2]
    if tx is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        to_target = -dist(nx, ny, tx, ty)
        away_opp = dist(nx, ny, ox, oy)
        attack = 0
        if resources and dist(nx, ny, tx, ty) == 0:
            attack = 1000
        val = 5 * to_target + 2 * away_opp + attack - 0.1 * dist(nx, ny, (w - 1) // 2, (h - 1) // 2)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]