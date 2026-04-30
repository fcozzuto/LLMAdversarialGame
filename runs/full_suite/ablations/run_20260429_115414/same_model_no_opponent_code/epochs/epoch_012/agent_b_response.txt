def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            valid.append((dx, dy))

    resources = observation.get("resources") or []
    res = [(int(p[0]), int(p[1])) for p in resources]

    # If no resources, aggressively contest: move toward opponent (but avoid obstacles).
    if not res:
        best = None
        bestv = -10**18
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, ox, oy)
            v = -d
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    best = None
    bestv = -10**18

    # New strategy: after each move, choose the resource that maximizes our advantage
    # versus the opponent (opponent distance - our distance), with slight preference for speed.
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        myd = None
        local_best = -10**18
        for rx, ry in res:
            myd2 = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd2
            # Encourage not only winning the race, but also doing it faster.
            v = adv * 5 - myd2
            if v > local_best:
                local_best = v
                myd = myd2
        # Small tie-break: avoid moves that increase distance to the currently best-adv resource.
        vfinal = local_best
        if vfinal > bestv:
            bestv = vfinal
            best = (dx, dy)

    return [best[0], best[1]] if best else [0, 0]