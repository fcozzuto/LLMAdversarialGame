def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    obst = {(p[0], p[1]) for p in obstacles}

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def obst_pen(nx, ny):
        if (nx, ny) in obst:
            return 10**9
        # Penalize being adjacent/close to obstacles
        pen = 0
        for px, py in obst:
            dd = d2(nx, ny, px, py)
            if dd == 0:
                return 10**9
            if dd <= 2:
                pen += 40
            elif dd <= 4:
                pen += 12
        return pen

    best = None
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue
        # Evaluate by best resource after this move
        score = -obst_pen(nx, ny)
        if resources:
            local_best = -10**18
            for rx, ry in resources:
                myd = d2(nx, ny, rx, ry)
                opd = d2(ox, oy, rx, ry)
                adv = opd - myd
                # Prefer resources we can reach sooner, but only via deterministic formula
                val = adv * 10 - myd
                if val > local_best:
                    local_best = val
            score += local_best
        else:
            # No resources: drift toward opponent's side to contest future spawns
            score += -(d2(nx, ny, ox, oy))
        # Deterministic tie-break: fixed order of deltas
        if score > best_score:
            best_score = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]