def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = obs_list if isinstance(obs_list, set) else set(tuple(p) for p in obs_list)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    targets = []
    for r in res:
        rx, ry = r
        if (rx, ry) not in obstacles:
            targets.append((rx, ry))
    if not targets:
        return [0, 0]

    best_t = None
    best_key = None
    for rx, ry in targets:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - sd, -sd, (-rx, -ry))
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        key = (nod - nsd, -nsd, (dx, dy))
        if best_mkey is None or key > best_mkey:
            best_mkey = key
            best_m = (dx, dy)

    return [best_m[0], best_m[1]]