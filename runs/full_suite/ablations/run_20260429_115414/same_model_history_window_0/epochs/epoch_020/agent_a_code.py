def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    resources = observation["resources"]
    def clamp(x, a, b):
        return a if x < a else b if x > b else x
    def dist(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) + abs(dy)
    if not resources:
        moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
        best = None
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
            v = dist(nx, ny, ox, oy)
            if (nx, ny) in obstacles:
                v -= 1000
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]
    best_target = None
    best_tv = -10**9
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        tv = (od - sd) * 10 - sd
        if (rx, ry) in obstacles:
            tv -= 10000
        if tv > best_tv:
            best_tv = tv
            best_target = (rx, ry)
    tx, ty = best_target
    best = (0, 0)
    bestv = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
            v = 0
            if (nx, ny) in obstacles:
                v -= 1000000
            sd = dist(nx, ny, tx, ty)
            od = dist(nx, ny, ox, oy)
            cur_sd = dist(sx, sy, tx, ty)
            v += (cur_sd - sd) * 50  # progress to target
            v += od * 2  # stay away from opponent
            # If target is adjacent, slightly prioritize stepping onto it
            if sd == 0:
                v += 10000
            # Avoid moving closer to opponent if we are not improving much
            if dist(sx, sy, ox, oy) <= od:
                v += 5
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
    return [best[0], best[1]]