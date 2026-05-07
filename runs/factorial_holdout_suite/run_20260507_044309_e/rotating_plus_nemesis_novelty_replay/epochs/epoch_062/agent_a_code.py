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

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    candidates = []
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer stealing: maximize opponent distance advantage vs our distance; break ties by smallest our distance,
        # and then by deterministic coordinate order.
        priority = (do - ds, -ds, -rx, -ry)
        candidates.append((priority, rx, ry))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    tx, ty = candidates[0][1], candidates[0][2]

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        # Also consider whether this move keeps us ahead on the currently most contested resource.
        # (Use the best candidate resource as proxy.)
        contested = candidates[0]
        cx, cy = contested[1], contested[2]
        d_self_c = cheb(nx, ny, cx, cy)
        d_opp_c = cheb(ox, oy, cx, cy)
        ahead = d_opp_c - d_self_c
        key = (ahead, -d_to_target, -nx, -ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]