def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cands = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            cands.append((dx, dy))

    if not cands:
        return [0, 0]

    def man(a, b, c, d):
        t = a - c
        if t < 0:
            t = -t
        u = b - d
        if u < 0:
            u = -u
        return t + u

    if resources:
        best = None
        for dx, dy in cands:
            nx, ny = sx + dx, sy + dy
            local_best = None
            for rx, ry in resources:
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                score = (od - sd) * 10 - sd
                if local_best is None or score > local_best:
                    local_best = score
            if best is None or local_best > best[0] or (local_best == best[0] and (dx, dy) < best[1]):
                best = (local_best, (dx, dy))
        return [best[1][0], best[1][1]]

    best = None
    for dx, dy in cands:
        nx, ny = sx + dx, sy + dy
        t = nx - ox
        if t < 0:
            t = -t
        u = ny - oy
        if u < 0:
            u = -u
        dist = t if t > u else u
        if best is None or dist < best[0] or (dist == best[0] and (dx, dy) < best[1]):
            best = (dist, (dx, dy))
    return [best[1][0], best[1][1]]