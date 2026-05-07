def choose_move(observation):
    def get2(key, d=(0, 0)):
        v = observation.get(key, d)
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return int(d[0]), int(d[1])

    sx, sy = get2("self_position")
    ox, oy = get2("opponent_position")
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh:
                obstacles.add((x, y))

    resources = []
    for it in observation.get("resources") or []:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def steps(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    ti = int(observation.get("turn_index", 0) or 0)

    scored = []
    best_self = None
    for rx, ry in resources:
        ds = steps(sx, sy, rx, ry)
        do = steps(ox, oy, rx, ry)
        edge = do - ds  # positive => we arrive earlier
        parity = (rx + ry + ti) & 1
        # prefer earlier, then closer; parity breaks ties deterministically
        tup = (edge, -ds, -parity, -rx, -ry)
        scored.append((tup, rx, ry))
        if best_self is None or tup > best_self[0]:
            best_self = (tup, rx, ry)

    scored.sort(reverse=True)
    top_tup, tx, ty = scored[0]
    # Adaptation: if opponent likely races our best target, switch to a target we can beat.
    # Otherwise, race the best target.
    nearest_rx, nearest_ry = best_self[1], best_self[2]
    ds_near = steps(sx, sy, nearest_rx, nearest_ry)
    do_near = steps(ox, oy, nearest_rx, nearest_ry)
    if do_near <= ds_near:
        for tup, rx, ry in scored:
            edge = tup[0]
            if edge > 0:
                tx, ty = rx, ry
                break

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    # If target is blocked and we are forced to step into an obstacle, just stay.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        return [0, 0]
    return [dx, dy]