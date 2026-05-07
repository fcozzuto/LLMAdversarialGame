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
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_res = None
    best_adv = None
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer earlier
        key = (adv, -ds, -rx, -ry)
        if best_adv is None or key > best_adv:
            best_adv = key
            best_res = (rx, ry)

    if best_res is None:
        return [0, 0]
    tx, ty = best_res

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        adv = d_opp - d_self
        # Prefer moves that reduce distance and keep advantage; slight tiebreak by direction to target
        align = -(abs(nx - tx) + abs(ny - ty))
        score = (adv, -d_self, align, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move