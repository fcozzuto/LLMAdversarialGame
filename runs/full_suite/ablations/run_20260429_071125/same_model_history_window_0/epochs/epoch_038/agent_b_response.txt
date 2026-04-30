def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    def clamp(a, lo, hi): 
        return lo if a < lo else hi if a > hi else a
    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    if not resources:
        # Drift toward center while avoiding obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx, cy
    else:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            val = 0
            val += 17 * myd - 7 * opd  # prefer resources closer than opponent
            if best is None or val < best[0]:
                best = (val, rx, ry)
        if best is None:
            tx, ty = (w - 1) // 2, (h - 1) // 2
        else:
            tx, ty = best[1], best[2]
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        overlap_pen = 25 if (nx, ny) == (ox, oy) else 0
        opp_dist = cheb(nx, ny, ox, oy)
        # Encourage faster collection and slightly safer spacing
        score = nd * 20 - opp_dist + overlap_pen
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]