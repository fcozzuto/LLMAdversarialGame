def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(p[0], p[1]) for p in obstacles}

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inside(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx*dx + dy*dy
    def penalty(nx, ny):
        p = 0
        if (nx, ny) in obst: return 10**9
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
            if (nx+dx, ny+dy) in obst: p += 5
        return p
    def score(nx, ny):
        p = -dist2(nx, ny, ox, oy)  # prefer staying away from opponent
        if resources:
            bx, by = resources[0][0], resources[0][1]
            best = dist2(nx, ny, bx, by)
            for r in resources[1:]:
                rx, ry = r[0], r[1]
                d = dist2(nx, ny, rx, ry)
                if d < best: best = d
            p += -best * 2
        else:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            p += -dist2(nx, ny, int(cx), int(cy))
        if (nx, ny) == (ox, oy): p -= 10**6
        return p - penalty(nx, ny)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inside(nx, ny): 
            continue
        s = score(nx, ny)
        if s > best_score or (s == best_score and (dx, dy) < best_move):
            best_score = s
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]