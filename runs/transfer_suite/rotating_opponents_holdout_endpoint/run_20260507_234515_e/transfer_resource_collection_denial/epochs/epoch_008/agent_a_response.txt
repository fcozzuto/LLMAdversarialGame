def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def safe(x, y):
        return inside(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    best_r = resources[0]
    best_ts = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd
        ts = lead * 1000000 - sd
        if best_ts is None or ts > best_ts:
            best_ts = ts
            best_r = (rx, ry)

    rx, ry = best_r
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        sd2 = cheb(nx, ny, rx, ry)
        od2 = cheb(ox, oy, rx, ry)
        lead2 = od2 - sd2

        # Small deterrent for getting stuck / far from any resource when lead is not positive
        nearest = None
        for (crx, cry) in resources:
            d = cheb(nx, ny, crx, cry)
            if nearest is None or d < nearest:
                nearest = d
        nearest = nearest if nearest is not None else 0

        val = lead2 * 1000000 - sd2
        if lead2 <= 0:
            val = val - nearest * 10

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]