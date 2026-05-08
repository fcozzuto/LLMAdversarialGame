def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))
    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    tr = int(observation.get("turns_remaining", 0))
    my_close_weight = 2 if tr > 4 else 1

    best_res = None
    best_adv = -10**9
    best_my_dist = 10**9
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = (opd - myd) * my_close_weight
        if adv > best_adv or (adv == best_adv and myd < best_my_dist):
            best_adv = adv
            best_my_dist = myd
            best_res = (rx, ry)

    if best_res is None:
        return [0, 0]
    rx, ry = best_res

    best_move = None
    best_score = -10**9
    for dx, dy, nx, ny in legal:
        myd = cheb(nx, ny, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        score = (opd - myd) * my_close_weight - myd
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score and best_move is not None:
            if cheb(nx, ny, rx, ry) < cheb(sx + best_move[0], sy + best_move[1], rx, ry):
                best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]