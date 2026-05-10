def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    obstacles = set()
    obs_list = observation.get("obstacles") or []
    for p in obs_list:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except:
            pass
    resources = observation.get("resources") or []
    res_cells = []
    for p in resources:
        try:
            x, y = p
            res_cells.append((int(x), int(y)))
        except:
            pass

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    target = None
    if res_cells:
        bestd = 10**9
        for rx, ry in res_cells:
            d = man(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                target = (rx, ry)
    best_score = -10**18
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if target is not None:
            score += -man(nx, ny, target[0], target[1])
        d_opp = man(nx, ny, ox, oy)
        score += d_opp * 0.7
        if d_opp == 0:
            score -= 1000
        if resources:
            for rx, ry in res_cells:
                if nx == rx and ny == ry:
                    score += 50
                    break
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move if best_move != [0, 0] or (sx, sy) not in obstacles else [0, 0]