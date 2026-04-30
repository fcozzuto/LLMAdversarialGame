def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs_set = {(p[0], p[1]) for p in obstacles}
    res_list = [(p[0], p[1]) for p in resources]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    cands = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs_set:
            cands.append((dx, dy, nx, ny))
    if not cands:
        return [0, 0]

    # If no visible resources, chase the opponent along anti-goal corner bias.
    if not res_list:
        tx, ty = (0, 7) if (ox > sx) else (7, 0)
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in cands:
            v = -kdist(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Choose move maximizing "win-likelihood" for capturing a resource sooner than opponent.
    # Tie-break deterministically by distance-to-resource and then by stable move ordering.
    best = None
    bestv = -10**18
    for dx, dy, nx, ny in cands:
        mv = -10**18
        for rx, ry in res_list:
            ds = kdist(nx, ny, rx, ry)
            do = kdist(ox, oy, rx, ry)
            # Higher when we are closer, and when opponent is farther; add small preference for closeness.
            v = (do - ds) * 100 - ds
            if v > mv:
                mv = v
        if mv > bestv:
            bestv = mv
            best = (dx, dy)
    return [int(best[0]), int(best[1])]