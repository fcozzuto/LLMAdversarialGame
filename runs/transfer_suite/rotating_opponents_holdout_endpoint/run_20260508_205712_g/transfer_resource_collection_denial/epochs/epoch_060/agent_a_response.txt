def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(int(x), int(y)) for x, y in obstacles}

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def pick_target(ax, ay):
        if not resources:
            return None
        best = None
        bestk = None
        for rx, ry in resources:
            d = man(ax, ay, rx, ry)
            # prefer resources where we are much closer than the opponent
            otd = man(ox, oy, rx, ry)
            advantage = otd - d  # larger is better for "we're closer"
            # deterministic tie-break: advantage desc, then d asc, then coords
            k = (-advantage, d, ry, rx)
            if bestk is None or k < bestk:
                bestk = k
                best = (rx, ry)
        return best

    target = pick_target(sx, sy)
    if target is None:
        # no resources: move away from opponent if possible
        tx, ty = sx, sy
        bestk = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            k = (-man(nx, ny, ox, oy), ny, nx)
            if bestk is None or k < bestk:
                bestk = k
                tx, ty = nx, ny
        return [tx - sx, ty - sy]

    rx, ry = target
    # choose move that gets us closest to target; lightly prefer moves that also keep away from opponent
    bestk = None
    best = (sx, sy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        k = (man(nx, ny, rx, ry), 0.05 * man(nx, ny, ox, oy), ny, nx)
        if bestk is None or k < bestk:
            bestk = k
            best = (nx, ny)

    nx, ny = best
    return [nx - sx, ny - sy]