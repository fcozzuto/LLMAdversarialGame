def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    resources = [tuple(p) for p in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if resources:
        best_r = None
        best_val = -10**18
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            val = (od - sd) * 1000 - sd
            if val > best_val:
                best_val = val
                best_r = (rx, ry)
        tx, ty = best_r
        best = None
        bestd = 10**18
        besttie = None
        for dx, dy, nx, ny in legal:
            d = man(nx, ny, tx, ty)
            key = (d, dx, dy)
            if d < bestd or (d == bestd and (besttie is None or key < besttie)):
                bestd = d
                besttie = key
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    best = None
    bestd = -1
    besttie = None
    for dx, dy, nx, ny in legal:
        d = man(nx, ny, ox, oy)
        key = (-d, dx, dy)
        if d > bestd or (d == bestd and (besttie is None or key < besttie)):
            bestd = d
            besttie = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])]