def choose_move(observation):
    W = observation.get("grid_width", 0)
    H = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if (x, y) not in obs:
                res.append((x, y))

    def inb(x, y):
        return (W == 0 or (0 <= x < W)) and (H == 0 or (0 <= y < H))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def pick_target():
        if not res:
            return None
        best = None
        bestv = -10**18
        for rx, ry in res:
            dv = -man(sx, sy, rx, ry) + 0.35 * man(ox, oy, rx, ry)
            if best is None or dv > bestv or (dv == bestv and (rx, ry) < best):
                bestv = dv
                best = (rx, ry)
        return best

    target = pick_target()
    if target is None:
        tx, ty = ox, oy
    else:
        tx, ty = target

    best_move = (0, 0)
    best_cost = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if target is None:
            cost = man(nx, ny, tx, ty)
        else:
            cost = man(nx, ny, tx, ty) - 0.05 * man(nx, ny, ox, oy)
        if cost < best_cost or (cost == best_cost and (dx, dy) < best_move):
            best_cost = cost
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [int(dx), int(dy)]