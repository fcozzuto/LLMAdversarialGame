def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(p[0], p[1]) for p in obstacles}
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None  # (exclusive_flag, margin, selfd, oppd, dx, dy)
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        exclusive_best = None
        for rx, ry in resources:
            selfd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            margin = oppd - selfd
            exclusive_flag = 1 if margin >= 2 else 0
            cand_key = (exclusive_flag, margin, selfd, oppd)
            if exclusive_best is None or cand_key > exclusive_best:
                exclusive_best = cand_key
        if exclusive_best is None:
            continue
        key = (exclusive_best[0], exclusive_best[1], -exclusive_best[2], -exclusive_best[3], dx, dy)
        if best is None or key > best:
            best = key

    if best is None:
        return [0, 0]
    return [best[4], best[5]]