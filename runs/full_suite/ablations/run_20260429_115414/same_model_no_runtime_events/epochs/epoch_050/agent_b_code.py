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
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    rem = observation.get("remaining_resource_count")
    try:
        rem = int(rem or 0)
    except:
        rem = 0
    late = rem <= 4

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_target = None
    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if late:
                key = (ds, rx, ry)
            else:
                adv = do - ds  # positive means we are closer in Chebyshev distance
                key = (-adv, ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        opp_target = (best[1], best[2])

    tx, ty = opp_target if opp_target is not None else (ox, oy)

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds = cheb(nx, ny, tx, ty)

        # If not late, add a denial term: prefer moves that keep opponent farther from our target
        if late:
            val = (ds, abs(nx - ox) + abs(ny - oy))
        else:
            do_next = cheb(ox, oy, tx, ty)
            # stronger preference when we are already advantaged; weaker otherwise to avoid over-commitment
            val = (ds - (do_next - ds) * 0.15, ds, -(do_next - ds))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]