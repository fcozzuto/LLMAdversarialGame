def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    res_set = set()
    for p in resources:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res_set.add((x, y))

    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        v = ax - bx
        if v < 0:
            v = -v
        u = ay - by
        if u < 0:
            u = -u
        return v + u

    if not resources:
        return [0, 0]

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in res_set:
            score = 10**12 - (man(nx, ny, ox, oy))
        else:
            score = -10**18
            for rx, ry in res_set:
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                # Prefer cells that make us closer than the opponent to some resource,
                # and prefer fast pickups.
                s = (od - sd) * 1000 - sd * 3
                if s > score:
                    score = s
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]