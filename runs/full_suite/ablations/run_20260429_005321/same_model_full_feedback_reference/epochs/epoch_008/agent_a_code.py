def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    me = (sx, sy)
    opp = (ox, oy)

    if not res:
        tx = w - 1 if ox > sx else 0
        ty = h - 1 if oy > sy else 0
        best = [0, 0]
        best_s = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            s = -dist((nx, ny), (tx, ty)) + 0.05 * (dist((nx, ny), opp) - dist(me, opp))
            if s > best_s:
                best_s = s
                best = [dx, dy]
        return [best[0], best[1]]

    best = [0, 0]
    best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        here = (nx, ny)
        my_d = min(dist(here, r) for r in res)
        op_d = min(dist(opp, r) for r in res)
        my_to_my_closest = min(res, key=lambda r: dist(here, r))
        opp_to_same = dist(opp, my_to_my_closest)
        adv = op_d - my_d  # positive means we are closer than opponent to some resource (relative)
        tie = -my_d + 0.08 * (opp_to_same - my_d) - 0.01 * dist(here, opp)
        s = adv * 2.0 + tie
        if s > best_s:
            best_s = s
            best = [dx, dy]

    return [int(best[0]), int(best[1])]