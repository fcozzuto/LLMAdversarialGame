def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_cell = None
    best_adv = None
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer in chebyshev
        key = (adv, -ds, -rx, -ry)
        if best_cell is None or key > best_adv:
            best_cell = (rx, ry)
            best_adv = key
    if best_cell is None:
        return [0, 0]

    tx, ty = best_cell
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        adv = no - ns
        on_resource = 1 if (nx, ny) == (tx, ty) else 0
        key = (on_resource, adv, -ns, -(abs(nx - ox) + abs(ny - oy)), -nx, -ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    if best_key is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]