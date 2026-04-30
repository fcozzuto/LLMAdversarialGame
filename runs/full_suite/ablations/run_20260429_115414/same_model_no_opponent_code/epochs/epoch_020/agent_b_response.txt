def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}

    resources = observation.get("resources") or []
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dcheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def obs_penalty(x, y):
        p = 0
        for ax in (x - 1, x, x + 1):
            for ay in (y - 1, y, y + 1):
                if (ax, ay) in obs:
                    p += 1
        return p

    # Target selection: prefer resources we're closer to than opponent, and closer overall.
    tx, ty = sx, sy
    best = None
    for rx, ry in resources:
        ds = dcheb(sx, sy, rx, ry)
        do = dcheb(ox, oy, rx, ry)
        # Higher is better: being relatively closer to the resource matters most.
        key = (do - ds) * 100 - ds
        if best is None or key > best:
            best = key
            tx, ty = rx, ry

    # Movement: greedy toward target while keeping opponent farther and away from obstacles.
    best_mv = (0, 0)
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ds2 = dcheb(nx, ny, tx, ty)
        do2 = dcheb(nx, ny, ox, oy)
        # Encourage reducing our distance to target; discourage moving near obstacles;
        # slightly prefer positions that are farther from the opponent.
        sc = -ds2 + 0.15 * do2 - 0.12 * obs_penalty(nx, ny)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)

    dx, dy = best_mv
    return [int(dx), int(dy)]