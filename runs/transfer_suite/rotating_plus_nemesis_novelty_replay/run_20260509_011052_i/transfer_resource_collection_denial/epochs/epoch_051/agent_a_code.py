def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def step_towards(tx, ty):
        dx = 0
        if tx > sx:
            dx = 1
        elif tx < sx:
            dx = -1
        dy = 0
        if ty > sy:
            dy = 1
        elif ty < sy:
            dy = -1
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            return [dx, dy]
        # Try alternative: prioritize x then y, then diagonal restrictions
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                nx, ny = sx + adx, sy + ady
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                    if cheb(nx, ny, tx, ty) < cheb(sx, sy, tx, ty):
                        return [adx, ady]
        return [0, 0]

    if not resources:
        tx, ty = ox, oy
        return step_towards(tx, ty)

    best = None
    best_key = (-10**18, -10**18, 10**18)
    for x, y in resources:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        # Prefer resources where we are closer than opponent; also prefer nearer targets
        gain = od - sd
        tie = 0
        if gain > 0:
            tie = 1000000
        key = (tie + gain, -sd, x + 10 * y)
        if key > best_key:
            best_key = key
            best = (x, y)

    tx, ty = best
    return step_towards(tx, ty)