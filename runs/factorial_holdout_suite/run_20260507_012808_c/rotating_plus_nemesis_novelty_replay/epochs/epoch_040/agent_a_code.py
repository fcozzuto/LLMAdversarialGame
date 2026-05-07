def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        dx = 0
        dy = 0
        for mx, my in [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]:
            nx = sx + mx; ny = sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cur = abs(nx - ox) + abs(ny - oy)
                best = abs(sx - ox) + abs(sy - oy)
                if cur > best:
                    dx = mx; dy = my
        return [dx, dy]

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_step = (0, 0)
    best_score = None
    for mx, my in deltas:
        nx = sx + mx; ny = sy + my
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        cur_best = None
        for tx, ty in resources:
            ds = man(nx, ny, tx, ty)
            do = man(ox, oy, tx, ty)
            val = ds - 0.6 * do - 0.01 * (tx + ty)
            if cur_best is None or val < cur_best:
                cur_best = val
        if cur_best is None:
            continue
        if best_score is None or cur_best < best_score:
            best_score = cur_best
            best_step = (mx, my)

    return [int(best_step[0]), int(best_step[1])]