def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    res_list = observation.get("resources") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in res_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    best = None
    bestv = -10**18
    for rx, ry in resources:
        sd = man(x, y, rx, ry)
        od = man(ox, oy, rx, ry)
        v = (od - sd) * 1000 - sd
        if v > bestv:
            bestv = v
            best = (rx, ry)

    tx, ty = best
    # Choose move that most reduces distance to our chosen target; tie-break by avoiding giving opponent advantage.
    cand = []
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not ok(nx, ny):
            continue
        sd2 = man(nx, ny, tx, ty)
        od2 = man(nx, ny, ox, oy)
        gain = -(sd2) * 1000 + od2  # prefer smaller sd2; discourage moving toward opponent
        cand.append((gain, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort(reverse=True)
    return [int(cand[0][1]), int(cand[0][2])]