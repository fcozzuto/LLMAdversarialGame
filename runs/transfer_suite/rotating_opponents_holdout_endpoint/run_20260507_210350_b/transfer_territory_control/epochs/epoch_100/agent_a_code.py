def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = observation.get("obstacles") or []
    obstacle_set = set()
    for o in obs:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = o[0], o[1]
            try:
                x, y = int(x), int(y)
            except Exception:
                continue
            if inb(x, y):
                obstacle_set.add((x, y))

    resources = observation.get("resources") or []
    res_cells = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            try:
                x, y = int(x), int(y)
            except Exception:
                continue
            if inb(x, y) and (x, y) not in obstacle_set:
                res_cells.append((x, y))

    opp_pos = observation.get("opponent_position")
    if isinstance(opp_pos, (list, tuple)) and len(opp_pos) >= 2:
        ox, oy = int(opp_pos[0]), int(opp_pos[1])
    else:
        ox, oy = w - 1, h - 1

    target = (ox, oy)
    best = None
    for (x, y) in res_cells:
        d = abs(x - sx) + abs(y - sy)
        if best is None or d < best[0] or (d == best[0] and (x, y) < best[1]):
            best = (d, (x, y))
    if best is not None:
        target = best[1]

    candidates = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best_move = None
    best_dist = None
    tx, ty = target
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacle_set:
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        if best_dist is None or dist < best_dist or (dist == best_dist and (dx, dy) < best_move):
            best_dist = dist
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]