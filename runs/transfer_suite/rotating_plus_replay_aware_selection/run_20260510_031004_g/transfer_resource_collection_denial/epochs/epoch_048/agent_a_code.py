def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_list:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    if not resources:
        return [0, 0]

    res_set = set()
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if 0 <= rx < w and 0 <= ry < h:
            res_set.add((rx, ry))

    if (sx, sy) in res_set:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0))
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    best = None
    best_key = None
    for (rx, ry) in res_set:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we're closer to; break ties deterministically.
        key = (-(od - sd), sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    best_move = None
    best_dist = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d = cheb(nx, ny, rx, ry)
        # Second objective: slightly avoid moving closer for enemy denial reversal.
        ed = cheb(nx, ny, ox, oy)
        key = (d, ed, nx, ny)
        if best_dist is None or key < best_dist:
            best_dist = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]