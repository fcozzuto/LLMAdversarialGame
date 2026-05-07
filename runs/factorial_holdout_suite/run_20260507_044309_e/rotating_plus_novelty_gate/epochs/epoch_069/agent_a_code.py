def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    res_set = set(tuple(r) for r in resources)
    for dx, dy, nx, ny in valid:
        if (nx, ny) in res_set:
            return [dx, dy]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    best = None
    best_score = None
    for rx, ry in resources:
        dme = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        winrace = do - dme
        opp_side = (ry > oy) if oy < h // 2 else (ry < oy)
        score = winrace * 100 - dme
        if opp_side:
            score += 15
        if best_score is None or score > best_score or (score == best_score and (rx, ry) < best):
            best_score = score
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    best_move = None
    best_mscore = None
    for dx, dy, nx, ny in valid:
        dnew = cheb(nx, ny, tx, ty)
        dold = cheb(sx, sy, tx, ty)
        progress = dold - dnew
        tie = abs(nx - tx) + abs(ny - ty)
        mscore = progress * 100 - dnew - tie * 0.001
        if best_mscore is None or mscore > best_mscore or (mscore == best_mscore and (dx, dy) < best_move):
            best_mscore = mscore
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]