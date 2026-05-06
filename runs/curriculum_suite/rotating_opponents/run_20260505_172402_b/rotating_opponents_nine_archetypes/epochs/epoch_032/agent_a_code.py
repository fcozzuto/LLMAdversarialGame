def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def mdist(a, b, x, y):
        dx = a - x
        if dx < 0: dx = -dx
        dy = b - y
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not res:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            v = mdist(ox, oy, nx, ny)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    oppd = mdist(ox, oy, sx, sy)
    threat = 1 if oppd <= 2 else 0

    # Choose move that advances toward best resource while keeping/creating separation from opponent.
    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        dres = 10**9
        for rx, ry in res:
            d = mdist(rx, ry, nx, ny)
            if d < dres:
                dres = d

        dop = mdist(ox, oy, nx, ny)
        # Prefer collecting lines of escape from corner-guard: if threatened, strongly maximize distance.
        v = (-1.2 * dres) + (1.0 * dop)
        if threat:
            v += 6.0 * dop
        # Avoid stepping closer to opponent than we are currently.
        if dop < oppd:
            v -= (oppd - dop) * (3.0 if threat else 1.5)

        # Mild obstacle avoidance: penalize moves with many blocked neighbors.
        blocked = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if not free(tx, ty):
                blocked += 1
        v -= blocked * 0.05

        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best