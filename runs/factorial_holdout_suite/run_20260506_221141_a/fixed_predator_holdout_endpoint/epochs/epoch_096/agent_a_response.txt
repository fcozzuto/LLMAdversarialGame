def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Filter invalid resource positions if needed
    res_list = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            res_list.append((rx, ry))
    if not res_list:
        return [0, 0]

    # If already on a resource, secure it.
    for rx, ry in res_list:
        if rx == sx and ry == sy:
            return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best = None
    best_key = None

    # Target scoring: prefer resources where we are closer than opponent; else nearest contested.
    for dx, dy, nx, ny in moves:
        local_best_key = None
        for rx, ry in res_list:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Higher is better: we want (od - sd) to be large; then smaller sd.
            key = (od - sd, -sd, -max(0, od - sd))
            if (local_best_key is None) or (key > local_best_key):
                local_best_key = key
        if local_best_key is None:
            continue
        if (best_key is None) or (local_best_key > best_key):
            best_key = local_best_key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]