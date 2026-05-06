def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set(tuple(p) for p in obstacles)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = [0, 0]
    bestv = None

    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def man(a, b, c, d):
        t = a - c
        if t < 0:
            t = -t
        u = b - d
        if u < 0:
            u = -u
        return t + u

    # Precompute nearest resource distances from candidate cell
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d_opp = man(nx, ny, ox, oy)
        d_ctr = man(nx, ny, cx, cy)

        d_res = None
        for r in resources:
            rx, ry = r
            d = man(nx, ny, rx, ry)
            if d_res is None or d < d_res:
                d_res = d

        if d_res is None:
            # No resources known: go toward center while avoiding opponent
            val = (d_ctr, -d_opp)
        else:
            # Prefer closer to resources and farther from opponent; slight center bias
            val = (d_res, -d_opp, d_ctr)

        if bestv is None or val < bestv:
            bestv = val
            best = [dx, dy]

    if not bestv and not blocked(sx, sy):
        return [0, 0]
    return best