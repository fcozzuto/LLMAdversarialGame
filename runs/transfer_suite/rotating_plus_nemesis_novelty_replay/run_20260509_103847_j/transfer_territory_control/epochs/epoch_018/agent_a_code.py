def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    un = observation.get("unclaimed_cells")
    if isinstance(un, list) and un:
        un_list = [(int(c[0]), int(c[1])) for c in un if isinstance(c, (list, tuple)) and len(c) >= 2]
        target = None
        bestd = 10**9
        for x, y in un_list:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd:
                bestd = d
                target = (x, y)
    else:
        target = (ox, oy)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    dirs = [(0, 0), (0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_score = -10**18
    tx, ty = target if target is not None else (ox, oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_op = abs(nx - ox) + abs(ny - oy)
        d_t = abs(nx - tx) + abs(ny - ty)
        score = -d_op - 0.5 * d_t
        if dx == 0 and dy == 0:
            score -= 0.1
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if not (-1 <= dx <= 1 and -1 <= dy <= 1):
        return [0, 0]
    if dx == 0 and dy == 0 and not valid(sx, sy):
        return [0, 0]
    return [int(dx), int(dy)]