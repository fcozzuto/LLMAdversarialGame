def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is None:
            continue
        try:
            x, y = p
        except Exception:
            continue
        obs.add((x, y))
    resources = observation.get("resources") or []

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def manhattan(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    target = None
    bestd = None
    if resources:
        for p in resources:
            if p is None:
                continue
            x, y = p
            if not inb(x, y):
                continue
            d = manhattan(sx, sy, x, y)
            if d == 0 or not free(sx, sy):
                pass
            if bestd is None or d < bestd or (d == bestd and (x, y) < target):
                bestd = d
                target = (x, y)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        if target is not None:
            dres = manhattan(nx, ny, target[0], target[1])
            dop = manhattan(nx, ny, ox, oy)
            score = -dres * 1000 - dop
        else:
            dop = manhattan(nx, ny, ox, oy)
            score = dop * 10
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]