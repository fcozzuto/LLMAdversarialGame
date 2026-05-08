def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = observation.get("obstacles") or []
    obstacles = set((int(x), int(y)) for x, y in obs)

    res = observation.get("resources") or []
    resources = [(int(x), int(y)) for x, y in res]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        v = a - c
        if v < 0:
            v = -v
        u = b - d
        if u < 0:
            u = -u
        return v + u

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best = (None, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d_opp = man(nx, ny, ox, oy)
        if resources:
            d_res = min(man(nx, ny, rx, ry) for rx, ry in resources)
            score = 100 * d_opp - d_res
        else:
            cx, cy = w // 2, h // 2
            score = 100 * d_opp - man(nx, ny, cx, cy)
        if score > best[1]:
            best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [best[0][0], best[0][1]]