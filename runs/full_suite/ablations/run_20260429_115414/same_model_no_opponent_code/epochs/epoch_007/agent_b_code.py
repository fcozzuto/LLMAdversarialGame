def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        obstacles.add((int(p[0]), int(p[1])))

    res_list = observation.get("resources", []) or []
    resources = []
    for p in res_list:
        resources.append((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if resources:
        best_res = None
        best_d = None
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if best_d is None or d < best_d or (d == best_d and (rx, ry) < best_res):
                best_d = d
                best_res = (rx, ry)
        tx, ty = best_res
    else:
        tx, ty = w // 2, h // 2

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(nx, ny, ox, oy)
        r_bonus = 0.0
        for rx, ry in resources:
            if nx == rx and ny == ry:
                r_bonus = 50.0
                break
        score = -ds + 0.25 * do + r_bonus
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]