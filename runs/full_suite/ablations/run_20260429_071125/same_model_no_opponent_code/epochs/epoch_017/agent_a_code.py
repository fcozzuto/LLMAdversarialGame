def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    occ = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            occ.add((int(p[0]), int(p[1])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_target = None
    best_lead = -10**18
    best_self = 10**18
    for p in resources:
        if p is None or len(p) < 2:
            continue
        rx, ry = int(p[0]), int(p[1])
        if not (0 <= rx < w and 0 <= ry < h):
            continue
        ds = cheb(x, y, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds
        if lead > best_lead or (lead == best_lead and (ds < best_self or (ds == best_self and (rx, ry) < best_target))):
            best_lead = lead
            best_self = ds
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]

    tx, ty = best_target
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = 10**18
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in occ:
            continue
        val = cheb(nx, ny, tx, ty)
        if val < best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in occ:
                return [dx, dy]
        return [0, 0]

    return [int(best[0]), int(best[1])]