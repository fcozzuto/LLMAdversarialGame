def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]

    obstacles_raw = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_raw:
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    best_target = None
    best_key = None
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # bigger is better
        key = (adv, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(nx, ny, ox, oy)  # proxy to avoid moving into opponent vicinity
        os = cheb(ox, oy, tx, ty)
        # Prefer getting closer to target, and preferring states where opponent is not closer.
        score = (os - ns, -ns, -no, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    # Fallback if every move blocked
    if best_score is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]