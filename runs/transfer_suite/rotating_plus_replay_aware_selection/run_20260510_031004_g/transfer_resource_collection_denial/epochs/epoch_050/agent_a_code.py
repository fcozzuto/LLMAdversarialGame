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

    res_set = set()
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if 0 <= rx < w and 0 <= ry < h:
            res_set.add((rx, ry))

    if (sx, sy) in res_set or not resources:
        return [0, 0]

    dirs = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best_r = None
    best_adv = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not (0 <= rx < w and 0 <= ry < h):
            continue
        if (rx, ry) in obs:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = ds - do  # smaller is better (more likely to arrive first)
        key = (adv, rx, ry)
        if best_r is None or key < (best_adv[0], best_adv[1], best_adv[2]):
            best_r = (rx, ry)
            best_adv = (adv, rx, ry)

    if best_r is None:
        return [0, 0]
    tx, ty = best_r

    cur_d = cheb(sx, sy, tx, ty)
    best_move = [0, 0]
    best_d = cur_d

    # Deterministic tie-breaking by move order already in dirs.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if d < best_d or (d == best_d and [dx, dy] < best_move):
            best_d = d
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]